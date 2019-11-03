from datetime import datetime, date, timedelta
from enum import Enum

class SpyOptionsTableSchema:
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
		self.starting_cash = starting_cash
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
		self.put_otm_offset = 2
		self.missed_weeks = 0



	def print_out(self):
		print('----------------------- Zeus Algorithm Stats -----------------------')

		print('Current cash is: ' + str(self.cash))
		print('Current number of SPY shares held: ')
		for item in self.shares_held:
			print(str(item))
		print('\n')

		print('Open positions:')
		for pos in self.open_positions:
			print(str(pos))
		print('\n')
		
		print('Trade History:')
		for pos in self.trade_history:
			print(str(pos))
		print('\n')

		total_income = self.premiums_collected + self.capital_gains_collected
		print('Premiums collected: ' + str(self.premiums_collected))
		print('Capital gains collected ' + str(self.capital_gains_collected))
		print('Total income: ' + str(total_income))
		print('Missed Weeks: ' +str(self.missed_weeks))
		print('Return percentage: ' + str((total_income/self.starting_cash)*100))

	def retrieveCall(self, quote_date, expiration_date, cost_basis):
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
				ORDER BY strike ASC
				limit 1
			'''
			cur.execute(
				sql, 
				(
					quote_date.isoformat(' '), 
					next_day.isoformat(' '), 
					'C', 
					expiration_date.isoformat(),
					cost_basis
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
				GROUP BY strike
				ORDER BY strike DESC, quote_datetime ASC
				limit 50;
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
	
	def choose_calls(self, shares, expiration_date):
		opened_positions = []
		unused_shares = []
		premium = 0
		# calls = self.retrieveCalls(self.current_date, friday_this_week.date())
		for item in shares:
			call = self.retrieveCall(self.current_date, expiration_date, item['cost_basis'])
			if call:
				call = call[0]
				premium += call[SpyOptionsTableSchema.BID]
				opened_positions.append({
					'contract': call,
					'contract_count': item['share_count'] / 100,
					'cost_basis': item['cost_basis']
				})
			else:
				self.missed_weeks += 1
				unused_shares.append(item)
		return (opened_positions, premium, unused_shares)

	def choose_puts(self, puts, put_chunks, put_otm_offset, cash_available):
		"""
			Given an array of puts and the cash available, this function executes
			the Zeus put choosing strategy. This put choosing strategy works like 
			this: puts are sold in groups of "put_chunks" size, out of the money.  
			How far out of the money is determined by put_otm_offset.

			Returns the opened positions, their cash liability, and the premium collected.
		"""
		premium = 0
		opened_positions = []
		cash_liability = 0
		offset_counter = 0
		enough_cash = True
		for put in puts:
			market_price = put[SpyOptionsTableSchema.UNDERLYING_ASK]
			strike = put[SpyOptionsTableSchema.STRIKE]

			# Put OTM is when the stock price is greater than the strike 
			if market_price > strike:
				if offset_counter < put_otm_offset:
					offset_counter += 1
					continue

				put_liability = strike * 100
				num_possible_puts = int(cash_available/put_liability)

				if num_possible_puts < put_chunks:
					chunk_liability = num_possible_puts * put_liability

					# At this point we're out of cash so we break
					enough_cash = False
				else:
					chunk_liability = put_liability * put_chunks
					num_possible_puts = put_chunks

				cash_liability += chunk_liability
				cash_available -= chunk_liability

				if num_possible_puts:
					premium += put[SpyOptionsTableSchema.BID] * 100 * num_possible_puts
					opened_positions.append({
						'contract': put,
						'contract_count': num_possible_puts
					})
				
				if not enough_cash:
					break
		
		
		return (opened_positions, cash_liability, premium)
					
	def tryToSellOptions(self):
		# This algorithm only sells weekly options, which are options sold
		# on Mondays that expire on the following Friday.  Thus it is assumed 
		# that today's date is a Monday
		friday_this_week = self.current_date + timedelta(days=4)

		# Trying to sell Covered Calls (CC)
		if len(self.shares_held) > 0:
			# Executing the Zeus call choosing strategy
			opened_positions, premium, unused_shares = self.choose_calls(self.shares_held, friday_this_week.date())
			if opened_positions:
				self.premiums_collected += premium
				self.open_positions += opened_positions
				self.shares_held = unused_shares


		# Trying to sell Covered Puts (CP)
		if self.cash > 0:
			puts = self.retrievePuts(self.current_date, friday_this_week.date())
			# Executing the Zeus put choosing strategy
			opened_positions, cash_liability, premium = self.choose_puts(
				puts,
				self.put_chunks,
				self.put_otm_offset,
				self.cash
			)
			if opened_positions:
				self.premiums_collected += premium
				self.open_positions += opened_positions
				self.cash -= cash_liability


	def getHighLow(self, date):
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
		"""
			This function checks if any open positions will be 
			exercised or will expire.  A covered put (CP) will be exercised
			if the market prices dips below the breakeven point.  A covered
			call (CC) will exercise if the market price goes above the
			breakeven point.
		"""
		todaysHighLow = self.getHighLow(self.current_date)
		
		
		if not todaysHighLow:
			return 
		high = todaysHighLow[2]
		low = todaysHighLow[3]
		
		
		positions_still_open = []
		for position in self.open_positions:
			contract = position['contract']
			contract_type = contract[SpyOptionsTableSchema.OPTION_TYPE]
			expiration = contract[SpyOptionsTableSchema.EXPIRATION]
			strike = contract[SpyOptionsTableSchema.STRIKE]
			share_count = 100 * position['contract_count'] # 100 shares per contract

			# Covered Put Positions
			if contract_type == 'P':
				breakeven =  strike - contract[SpyOptionsTableSchema.BID]

				# CP expired worthless
				if self.current_date > datetime.fromisoformat(expiration): 
					self.cash += strike * share_count
					position['result'] = 'expired worthless'
					self.trade_history.append(position)
				elif low < breakeven:  # CP exercised
					self.shares_held.append({
						'share_count': share_count,
						'cost_basis': strike
					})
					position['result'] = 'exercised'
					self.trade_history.append(position)
				else: # Nothing happens to CP yet
					positions_still_open.append(position)

			else: # Covered Call Positions
				breakeven =  strike + contract[SpyOptionsTableSchema.BID]
				cost_basis = position['cost_basis']

				# CC expired worthless
				if self.current_date > datetime.fromisoformat(expiration): 
					self.shares_held.append({
						'share_count': share_count,
						'cost_basis': cost_basis
					})
					position['result'] = 'expired worthless'
					self.trade_history.append(position)
				elif high > breakeven:  # CC exercised
					capital_returned = strike * share_count
					capital_invested = cost_basis * share_count
					self.capital_gains_collected += capital_returned - capital_invested
					self.cash += capital_returned
					position['result'] = 'exercised'
					self.trade_history.append(position)
				else: # Nothing happens to CC yet
					positions_still_open.append(position)

			self.open_positions = positions_still_open
			

	def run(self):
		while self.current_date <= self.end_date:
			# Checks open positions to see if any will be
			# exercised or will expire
			if self.open_positions:
				self.checkOpenPositions()

			# Check if the day is Monday (weekday() value is 0), 
			# which is the day the algo sells options. 
			if self.current_date.weekday() == 0:
				self.tryToSellOptions()

				
			# Moving to the next day
			self.current_date += timedelta(days=1)
