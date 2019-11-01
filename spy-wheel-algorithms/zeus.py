from datetime import datetime, date, timedelta

class SpyOptionsTableSchema(Enum):
	QUOTE_DATETIME = 0
	EXPIRATION = 1
	STRIKE = 2
	OPTION_TYPE = 3
	BID = 4
	ASK = 5
	UNDERLYING_BID = 6
	UNDERLYING_ASK = 7

class Zeus:
	"""
		
	"""

	def __init__(self, starting_cash, start_date, end_date, db_conn):
		self.cash = starting_cash
		self.shares_held = []
		self.premiums_collected = 0
		self.capital_gains_collected = 0
		self.open_positions = []
		self.trade_history = []
		self.current_date = datetime.fromisoformat(start_date)
		self.end_date = datetime.fromisoformat(end_date)
		self.db_conn = db_conn
		self.put_chunks = 4
		self.put_otm_offset = 1



	def print_out(self):
		print('Zeus Algorithm')

		print('Current cash is: ' + str(self.cash))
		print('Current number of SPY shares held: ') # TODO

		print('Open positions:')
		for pos in self.open_positions:
			print(str(pos))
		print('\n')
		
		print('Trade History:')
		for pos in self.trade_history:
			print(str(pos))
		print('\n')

		print('Premiums collected: ' + str(self.premiums_collected))
		print('Capital gains collected ' + str(self.capital_gains_collected))
		print('Total income: ' + str(self.premiums_collected + self.capital_gains_collected))

	def retrieveCalls(self, quote_date, expiration_date, share_cost):
		next_day = quote_date + timedelta(days=1)
		with self.db_conn as conn:
			cur = conn.cursor()
			sql = ''' 
				SELECT * FROM spy_options_data
				WHERE quote_datetime >= ?
				AND quote_datetime < ?
				AND option_type = ?
				AND expiration = ?
				AND strike > ?
				ORDER BY strike, quote_datetime
			'''
			cur.execute(
				sql, 
				(
					quote_date.isoformat(' '), 
					next_day.isoformat(' '), 
					'C', 
					expiration_date.isoformat(),
					share_cost
				)
			)
			rows = cur.fetchall()
			return rows

	
	def retrievePuts(self, quote_date, expiration_date):
		next_day = quote_date + timedelta(days=1)
		with self.db_conn as conn:
			cur = conn.cursor()
			sql = ''' 
				SELECT * FROM spy_options_data
				WHERE quote_datetime >= ?
				AND quote_datetime < ?
				AND option_type = ?
				AND expiration = ?
				AND strike < underlying_bid
				ORDER BY strike DESC, quote_datetime ASC
				limit 200;
			'''
			cur.execute(
				sql, 
				(
					quote_date.isoformat(' '), 
					next_day.isoformat(' '), 
					'P', 
					expiration_date.isoformat()
				)
			)
			rows = cur.fetchall()
			return rows
	
	def choose_call(self, calls, shares):
		pass

	def choose_puts(self, puts):
		"""
			This put choosing strategy works like this: puts are sold in groups
			of "put_chunks" size, out of the money.  How far out of the money is 
			determined by put_otm_offset.
		"""
		print('-----------------------------')
		
		offset_counter = 0
		have_enough_cash = True
		while have_enough_cash:
			for put in puts:
				market_price = put[SpyOptionsTableSchema.UNDERLYING_ASK]
				strike = put[SpyOptionsTableSchema.STRIKE]

				# Put OTM is when the stock price is greater than the strike 
				if market_price > strike:
					if offset_counter < self.put_otm_offset:
						offset_counter += 1
						continue
					put_liability = underlying_ask * 100
					num_possible_puts = int(self.cash/put_liability)
					if num_possible_puts < self.put_chunks:
						self.cash = self.cash - (num_possible_puts * put_liability)
						have_enough_cash = False
					else:
						self.cash = self.cash - (put_liability * self.put_chunks)
					
		
		# class SpyOptionsTableSchema(Enum):
		# 	QUOTE_DATETIME = 0
		# 	EXPIRATION = 1
		# 	STRIKE = 2
		# 	OPTION_TYPE = 3
		# 	BID = 4
		# 	ASK = 5
		# 	UNDERLYING_BID = 6
		# 	UNDERLYING_ASK = 7
		# for put in puts:
		# 	print(put)
		# print(puts)
		return None
	
	def tryToSellOptions(self):
		# This algorithm only sells weekly options, which are options sold
		# on Mondays that expire on the following Friday.  Thus it is assumed 
		# that today's date is a Monday
		friday_this_week = self.current_date + timedelta(days=4)

		# Trying to sell Covered Calls (CC)
		if len(self.shares_held) > 0:
			calls = self.retrieveCalls(self.current_date, friday_this_week.date())

			# Executing the Zeus call choosing strategy
			chosen_calls = self.choose_calls(calls, self.shares_held)
			if chosen_calls:
				self.open_positions + chosen_calls

			# call_closest_to_money = None
			# for strike in calls:
			# 	call_closest_to_money = calls[strike][0]
			# 	break
			# self.open_positions.append(
			# 	{
			# 		'type': 'CC', 
			# 		'contracts_num': num_possible_contracts, 
			# 		'contract': call_closest_to_money,
			# 		'share_cost': self.share_cost
			# 	}
			# )
			# self.share_count = 0 # Setting to 0 because these shares are now spoken for (temporarily)

		# Trying to sell Covered Puts (CP)
		if self.cash > 0:
			puts = self.retrievePuts(self.current_date, friday_this_week.date())

			# Executing the Zeus put choosing strategy
			chosen_puts = self.choose_puts(puts)
			if chosen_puts:
				self.open_positions + chosen_puts

			# Just grabbing the put contracts at the first quote time
			# available, since that is all we need
			# puts_first_quote_time = None
			# for quote in puts:
			# 	puts_first_quote_time = puts[quote]
			# 	break

			# # Want to start at a specified offset "out of the money"
			# strike_offset, offset_counter = 1, 0
			
			# for put in puts_first_quote_time:
				# strike = put[2]
				# if offset_counter < strike_offset:
				# 	offset_counter += 1
				# 	continue
			
				# liability = strike * 100 # 100 shares per contract
				# num_contracts_per_strike = 4 # Particular detail of strategy
				# num_contracts_sold_at_strike = 0
				# while liability < self.cash and num_contracts_sold_at_strike < num_contracts_per_strike:
				# 	self.open_positions.append(
				# 		{
				# 			'type': 'CP', 
				# 			'contracts_num': 1, 
				# 			'contract': put
				# 		}
				# 	)
				# 	self.cash -= liability
				# 	num_contracts_sold_at_strike += 1

	def getTodaysHighLow(self):
		with self.db_conn as conn:
			cur = conn.cursor()
			sql = ''' 
				SELECT * FROM spy_stock_data
				WHERE date = ?
			'''
			cur.execute(sql, (self.current_date.date().isoformat(),))
			rows = cur.fetchall()
			if len(rows) > 0:
				return rows[0]
			else: 
				return None

	
	def checkOpenPositions(self):
		todaysHighLow = self.getTodaysHighLow()

		if not todaysHighLow:
			return 
		
		high = todaysHighLow[2]
		low = todaysHighLow[3]
		for item in self.open_positions:
			contract = item['contract']
			contract_type = ['type']
			strike = contract[2]
			premium = contract[4]
			expiration = contract[1]
			breakeven = strike + premium

			if contract_type == 'CC' and (high > breakeven or self.current_date >= expiration):
				self.premiums_collected += premium
				self.cash += premium
				if high > breakeven: # in this case the CC is exercised
					# self.
					pass
				elif self.current_date >= expiration: # in this case the CC expires worthless
					self.premiums_collected += premium
					self.cash += premium

				
			else:
				pass

			print('HERE')
			print(todaysHighLow)
		# for item in self.open_positions:
			
				




	def run(self):
		while self.current_date <= self.end_date:

			t = False

			# Check if the day is Monday (weekday() value is 0), 
			# which is the day the algo sells options. 
			if self.current_date.weekday() == 0:
				self.tryToSellOptions()
				t = True
				
			print(self.current_date)
			print(self.open_positions)
			if t:
				break
			# Checks open positions to see if any will be
			# exercised or will expire
			self.checkOpenPositions()

			# Moving to the next day
			self.current_date += timedelta(days=1)