class Zeus:
	"""
		
	"""

	def __init__(self, starting_cash):
		self.cash = starting_cash
		self.share_count = 0
		self.premiums_collected = 0
		self.capital_gains_collected = 0
		self.open_positions = [[60, 7], [10, 101]]
		self.closed_positions = [[2, 3], [4, 5]]



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



	def run(self, data_row, cash_infusion, sell_out=False):
		pass
