import datetime
import queue

from data_utils import DataUtils
from market_position import MarketPosition

class Zeus():
	"""
		Buys in the beginning, sells whenever sell_percent% up and then re-buys when 
		buy_percent% down from 30 day moving high
	"""

	def __init__(self, first_day, starting_cash, sell_percent, buy_percent):
		date = DataUtils.get_date_from_row(first_day)
		low = DataUtils.get_low_from_row(first_day)
		high = DataUtils.get_high_from_row(first_day)
	
		self.market_positions = [MarketPosition(date, low, starting_cash)]
		self.cash = 0
		self.sell_percent = 1 + sell_percent
		self.buy_percent = 1 - buy_percent

		self.thirty_day_queue = queue.PriorityQueue()
		self.insert_high_into_30_day_queue(high, date)

		self.watch_period = 30
		self.counter = 1

	def insert_high_into_30_day_queue(self, high, date):
		"""
			Inserts a new high into the queue and does any 
			necessary housekeeping.
		"""

		# Reformatting the buy date from a string like 
		# '2017-01-17' to a datetime object
		date_format = '%Y-%m-%d'
		date_obj = datetime.datetime.strptime(date, date_format)


		# Removing all data from more than 30 days ago
		cutoff_date = date_obj - datetime.timedelta(days=30)
		while self.thirty_day_queue.qsize() > 0 and self.thirty_day_queue.queue[0][1] < cutoff_date:
			self.thirty_day_queue.get()
		
		# Making high negative in order to make the 
		# queue act like a max priority queue
		self.thirty_day_queue.put((-high, date_obj))

	def run(self, data_row, cash_infusion, sell_out=False):
		close = DataUtils.get_close_from_row(data_row)
		high = DataUtils.get_high_from_row(data_row)
		low = DataUtils.get_low_from_row(data_row)
		date = DataUtils.get_date_from_row(data_row)
		self.cash += cash_infusion

		self.insert_high_into_30_day_queue(high, date)

		# Checking if algo should sell out of any market positions
		temp = []
		for mp in self.market_positions:
			if sell_out or (high / mp.buy_price) >= self.sell_percent: 
				self.cash += mp.sell(date, high)
			else:
				temp.append(mp)
		self.market_positions = temp



		# Checking if algo should buy into the market
		if not sell_out:
			if self.counter < self.watch_period:
				self.counter += 1
			else:
				thirty_day_high = self.thirty_day_queue.queue[0][0]
				if (low / thirty_day_high) <= self.buy_percent:
					new_market_position = MarketPosition(date, low, self.cash)
					self.market_positions.append(new_market_position)
					self.cash = 0

		# Getting current balance (market positions + cash)
		balance = self.cash
		for mp in self.market_positions:
			balance += mp.current_value(high)

		return balance	

