from data_utils import DataUtils
from market_position import MarketPosition


class BuyAndHold():

	def __init__(self, first_day, starting_cash):
		self.market_positions = [MarketPosition(
			DataUtils.get_date_from_row(first_day), 
			DataUtils.get_low_from_row(first_day),
			starting_cash
		)]

	def run(self, data_row, cash_infusion, sell_out=False):
		high = DataUtils.get_high_from_row(data_row)
		low = DataUtils.get_low_from_row(data_row)
		date = DataUtils.get_date_from_row(data_row)
		
		if cash_infusion > 0:
			new_market_position = MarketPosition(date, low, cash_infusion)
			self.market_positions.append(new_market_position)

		balance = 0
		for mp in self.market_positions:			
			if sell_out:
				balance += mp.sell(date, high)
			else:
				balance += mp.current_value(high)

		return balance


