#!/usr/local/bin/python3
import json
import requests

# Third-party library: https://github.com/AndrewRPorter/yahoo-historical
from yahoo_historical import Fetcher

from data_utils import DataUtils
from market_position import MarketPosition



def get_data_from_api(symbol, start_date, end_date):
	fetcher = Fetcher(symbol, start_date, end_date)
	data = fetcher.getHistorical()
	return data
	

fetcher = Fetcher('AAPL', [1990, 1, 1], [2017, 9, 21])
data = get_data_from_api('AAPL', [1990, 1, 1], [2017, 9, 21])


	


"""
for index, row in data.iterrows():
	print(index)
	print(row)
	print('-'*20)
	#row.iloc[0]['Date']

print(data[1:2].iloc[1]['Date'])
"""


# Inputs
starting_cash = 20000

# Buy and hold algorithm
def buy_and_hold(starting_cash, data):
	data_rows = DataUtils.get_rows(data, 0)
	
	# Buying in at the very beginning
	first_row = data_rows[0]
	market_position = MarketPosition(
		DataUtils.get_date_from_row(first_row), 
		DataUtils.get_low_from_row(first_row),
		starting_cash
	)

	# Selling out at the end
	last_row = data_rows[-1]
	balance = market_position.sell(
		DataUtils.get_date_from_row(last_row),
		DataUtils.get_high_from_row(last_row)
	)

	return balance

# Buys in the beginning, sells whenever 5% up and then re-buys when 
# 3% down from 30 day moving high
def zeus(starting_cash, data):
	balance = starting_cash
	watch_period = 30
	counter = 1
	sell_percent = 1.05
	buy_percent = 0.97
	

	# Buying in on the first day
	first_row = DataUtils.get_rows(data, 0, 1)[0]
	high_so_far = DataUtils.get_high_from_row(first_row)
	market_position = MarketPosition(
		DataUtils.get_date_from_row(first_row), 
		DataUtils.get_low_from_row(first_row),
		starting_cash
	)

	for index, row in DataUtils.get_row_iterable(data, 1):
		close = DataUtils.get_close_from_row(row)
		high = DataUtils.get_high_from_row(row)
		low = DataUtils.get_low_from_row(row)
		date = DataUtils.get_date_from_row(row)

		if high > high_so_far:
			high_so_far = high

		if counter < watch_period:
			counter += 1
		else:
			if market_position:
				if (high / market_position.buy_price) >= sell_percent: 
					balance = market_position.sell(date, high)
					market_position = None
			else: 
				if (low/high_so_far) <= buy_percent:
					market_position = MarketPosition(date, low, balance)
					

	return balance

	

buy_and_hold_results = buy_and_hold(starting_cash, data)
zeus_results = zeus(starting_cash, data)


print('The starting cas amount is: '+str(starting_cash))
print()
print('Results')
print('-'*20)
print('buy_and_hold: \t' + str(buy_and_hold_results))
print('zeus: \t\t' + str(zeus_results))




