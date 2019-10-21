from datetime import datetime, date, timedelta

class Zeus:
	"""
		
	"""

	def __init__(self, starting_cash, start_date, end_date, db_conn):
		self.cash = starting_cash
		self.share_count = 0
		self.premiums_collected = 0
		self.capital_gains_collected = 0
		self.open_positions = []
		self.trade_history = []
		self.current_date = datetime.fromisoformat(start_date)
		self.end_date = datetime.fromisoformat(end_date)
		self.db_conn = db_conn
		self.share_price = 0



	def print_out(self):
		print('Zeus Algorithm')

		print('Current cash is: ' + str(self.cash))
		print('Current number of SPY shares held: ' + str(self.share_count) + '\n')

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

	def retrieveCalls(self, quote_date, expiration_date, share_price):
		print(quote_date)
		print(expiration_date)
		next_day = quote_date + timedelta(days=1)
		calls = {}
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
					share_price
				)
			)
			rows = cur.fetchall()
			STRIKE_INDEX = 2
			for row in rows:
				if row[STRIKE_INDEX] in calls:
					calls[row[STRIKE_INDEX]].append(row)
				else:
					calls[row[STRIKE_INDEX]] = [row]
		return calls

	
	def retrievePuts(self, quote_date, expiration_date):
		next_day = quote_date + timedelta(days=1)
		puts = {}
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
			STRIKE_INDEX = 2
			for row in rows:
				if row[STRIKE_INDEX] in puts:
					puts[row[STRIKE_INDEX]].append(row)
				else:
					puts[row[STRIKE_INDEX]] = [row]
		return puts
	
	def tryToSellOptions(self):
		# This algorithm only sells weekly options, which are options sold
		# on Mondays that expire on the following Friday.  Thus it is assumed 
		# that today's date is a Monday
		friday_this_week = self.current_date + timedelta(days=4)

		# Trying to sell Covered Calls (CC)
		num_possible_contracts = int(self.share_count / 100)
		if num_possible_contracts >= 1:
			calls = self.retrieveCalls(self.current_date, friday_this_week.date(), self.share_price)
			call_closest_to_money = None
			for strike in calls:
				call_closest_to_money = calls[strike][0]
				break
			self.open_positions.append(
				{
					'type': 'CC', 
					'contracts_num': num_possible_contracts, 
					'contract': call_closest_to_money
				}
			)
			self.share_count = 0 # Setting to 0 because these shares are now spoken for (temporarily)

		# Trying to sell Covered Puts (CP)
		if self.cash > 0:
			puts = self.retrievePuts(self.current_date, friday_this_week.date())
			strike_offset, offset_counter = 1, 0
			for strike in puts:
				# Want to start at a specified offset "out of the money"
				if offset_counter < strike_offset:
					print(strike)
					print(puts[strike])
					offset_counter += 1
					continue
			
				liability = strike * 100 # 100 shares per contract
				num_contracts_per_strike = 4 # Particular detail of strategy
				num_contracts_sold_at_strike = 0
				while liability < self.cash and num_contracts_sold_at_strike < num_contracts_per_strike:
					self.open_positions.append(
						{
							'type': 'CP', 
							'contracts_num': 1, 
							'contract': puts[strike][0]
						}
					)
					self.cash -= liability
					num_contracts_sold_at_strike += 1
				




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
			# Checks open contracts to see if any will be
			# exercised or will expire
			# self.checkOpenContracts()

			# Moving to the next day
			self.current_date += timedelta(days=1)