from data_utils import DataUtils
from market_position import MarketPosition


class BuyEveryDayAndHold():

	def __init__(self, first_day, starting_cash):
		self.market_positions = [MarketPosition(
			DataUtils.get_date_from_row(first_day), 
			DataUtils.get_low_from_row(first_day),
			starting_cash
		)]
		self.cash = 0

	def run(self, data_row, cash_infusion, sell_out=False):
		high = DataUtils.get_high_from_row(data_row)
		low = DataUtils.get_low_from_row(data_row)
		date = DataUtils.get_date_from_row(data_row)

		if cash_infusion > 0:
			self.cash += cash_infusion
			self.amount_to_invest_per_day = self.cash / 30

		if self.cash > 0:
			if self.cash > self.amount_to_invest_per_day:
				new_market_position = MarketPosition(date, low, self.amount_to_invest_per_day)
				self.cash -= self.amount_to_invest_per_day
			else:
				new_market_position = MarketPosition(date, low, self.cash)
				self.cash = 0
			self.market_positions.append(new_market_position)

		balance = 0
					
		if sell_out:
			for mp in self.market_positions:
				balance += mp.sell(date, high)
		else:
			for mp in self.market_positions:
				balance += mp.current_value(high)

		return balance


