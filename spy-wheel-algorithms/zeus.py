from datetime import date, timedelta

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
		self.current_date = date.fromisoformat(start_date)
		self.end_date = date.fromisoformat(end_date)
		self.db_conn = db_conn



	def print_out(self):
		print('Zeus Algorithm')

		print('Current cash is: ' + str(self.cash))
		print('Current number of SPY shares held: ' + str(self.share_count) + '\n')

		print('Open positions:')
		for pos in self.open_positions:
			print(str(pos))
		print('\n')
		
		print('Closed positions:')
		for pos in self.closed_positions:
			print(str(pos))
		print('\n')

		print('Premiums collected: ' + str(self.premiums_collected))
		print('Capital gains collected ' + str(self.capital_gains_collected))
		print('Total income: ' + str(self.premiums_collected + self.capital_gains_collected))

	def retrieveCoveredCalls(self):
		with self.db_conn:
			cur = conn.cursor()
			sql = ''' 
				SELECT * FROM spy_options_data
				WHERE quote_datetime >= ?
				AND quote_datetime
				INSERT INTO spy_stock_data
				VALUES (?,?,?,?,?)
			'''
			cur.executemany(sql, shaped_data)

	def tryToSellOptions(self):

		# Trying to sell Covered Calls
		if self.share_count > 0:
			num_contracts = self.share_count / 100


	def run(self):

		while self.current_date <= self.end_date:
			print('Starting cash is: ' + str(self.cash))

			# Check if the day is Monday (weekday() value is 0), 
			# which is the day the algo sells options. 
			if self.current_date.weekday() == 0:
				self.tryToSellOptions()

			# Checks open contracts to see if any will be
			# exercised or will expire
			self.checkOpenContracts()

			# Moving to the next day
			self.current_date += timedelta(days=1)