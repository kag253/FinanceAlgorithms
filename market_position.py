from datetime import datetime

class MarketPosition():
	"""
		Encapsulates all the data and functionality for
		a position in the stock market.
	"""


	def __init__(self, buy_date, buy_price, amount):
		"""Initializes the market position, aka 'buys in' to the market."""
		self.buy_price = buy_price
		self.amount = amount
		self.num_shares = amount / buy_price

		# Reformatting the buy date from a string like 
		# '2017-01-17' to a datetime object
		self.date_format = '%Y-%m-%d'
		self.buy_date = datetime.strptime(buy_date, self.date_format)

		# Setting default values for calculating taxes on profits
		self.short_term_capital_gains_tax = 0.33
		self.long_term_capital_gains_tax = 0.15
		self.long_term_duration = 365



	def sell(self, sell_date, sell_price, share_num_to_sell=None):
		"""Sells out the current market position."""

		# If the number of shares is not specified, we
		# sell everything
		if share_num_to_sell is None:
			share_num_to_sell = self.num_shares

		# Reformatting the sell date from a string like 
		# '2017-01-17' to a datetime object
		sell_date = datetime.strptime(sell_date, self.date_format)

		self.num_shares -= share_num_to_sell
		sell_amount = share_num_to_sell * sell_price

		# Calculating taxes if a profit was made on this trade
		profit = sell_amount - (share_num_to_sell * self.buy_price)
		taxes = 0
		if profit > 0:
			position_duration = sell_date - self.buy_date
			if position_duration.days >= self.long_term_duration:
				taxes = profit * self.long_term_capital_gains_tax
			else:
				taxes = profit * self.short_term_capital_gains_tax
		
		return round(sell_amount - taxes, 2)

	def long_term_tax_rate_eligible(self, sell_date):
		"""
			Determines if the current market position is 
			mature enough to be eligible for the lower
			long-term capital gains tax rate.
		"""

		# Reformatting the sell date from a string like 
		# '2017-01-17' to a datetime object
		sell_date = datetime.strptime(sell_date, self.date_format)
		position_duration = sell_date - self.buy_date
		return position_duration.days >= self.long_term_duration


	def num_shares(self):
		"""Returns the number of shares in this market position."""
		return self.num_shares

	def current_value(self, stock_price):
		"""Returns the current value of this market position."""
		return self.num_shares * stock_price

