from data_utils import DataUtils
from market_position import MarketPosition


class Zeus():
	"""
		Buys in the beginning, sells whenever 5% up and then re-buys when 
		3% down from 30 day moving high
	"""

	def __init__(self, first_day, starting_cash):
		self.high_so_far = DataUtils.get_high_from_row(first_day)
		self.market_position = MarketPosition(
			DataUtils.get_date_from_row(first_day), 
			DataUtils.get_low_from_row(first_day),
			starting_cash
		)
		self.balance = starting_cash
		self.watch_period = 30
		self.counter = 1
		self.sell_percent = 1.05
		self.buy_percent = 0.97


	def run(self, data_row, cash_infusion, sell_out=False):
		close = DataUtils.get_close_from_row(data_row)
		high = DataUtils.get_high_from_row(data_row)
		low = DataUtils.get_low_from_row(data_row)
		date = DataUtils.get_date_from_row(data_row)

		if sell_out:
			self.balance = self.market_position.sell(date, high)
		else:
			if high > self.high_so_far:
				self.high_so_far = high

			if self.counter < self.watch_period:
				self.counter += 1
			else:
				if self.market_position:
					if (high / self.market_position.buy_price) >= self.sell_percent: 
						self.balance = self.market_position.sell(date, high)
						self.market_position = None
				else: 
					if (low/self.high_so_far) <= self.buy_percent:
						self.market_position = MarketPosition(date, low, self.balance)

		return self.balance
					
