from data_utils import DataUtils
from market_position import MarketPosition


class BuyAndHold():

	def __init__(self, first_day, starting_cash):
		self.market_position = MarketPosition(
			DataUtils.get_date_from_row(first_day), 
			DataUtils.get_low_from_row(first_day),
			starting_cash
		)

	def run(self, data_row, cash_infusion, sell_out=False):
		stock_price = DataUtils.get_high_from_row(data_row)
		date = DataUtils.get_date_from_row(data_row)
		if sell_out:
			balance = self.market_position.sell(date, stock_price)
		else:
			balance = self.market_position.current_value(stock_price)
		return balance


