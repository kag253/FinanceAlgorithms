#!/usr/local/bin/python3
import json
import requests

# Third-party library: https://github.com/AndrewRPorter/yahoo-historical
from yahoo_historical import Fetcher

from data_utils import DataUtils



def get_data_from_api(symbol, start_date, end_date):
	fetcher = Fetcher(symbol, start_date, end_date)
	data = fetcher.getHistorical()
	return data
	

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
def run_buy_and_hold_algo(starting_cash, data):
	balance = starting_cash
	num_shares = starting_cash / DataUtils.get_low_from_row(DataUtils.get_rows(data, 0, 1))

	for index, row in DataUtils.get_row_iterable(data, 1):
		balance = num_shares * DataUtils.get_close_from_row(row)

	return balance

# Buys in the beginning, sells whenever 5% up and then re-buys when 
# 3% down from 30 day moving high
def zeus_algo(starting_cash, data):
	balance = starting_cash
	avail_cash = 0
	watch_period = 30
	counter = 1
	sell_percent = 1.05
	high_so_far = buy_in_price = first_low = DataUtils.get_low_from_row(DataUtils.get_rows(data, 0, 1))
	num_shares = starting_cash / first_low

	money_in_market = True

	for index, row in DataUtils.get_row_iterable(data, 1):
		close = DataUtils.get_close_from_row(row)
		high = DataUtils.get_high_from_row(row)
		low = DataUtils.get_low_from_row(row)

		if high > high_so_far:
			high_so_far = high

		if counter < watch_period:
			counter += 1
		else:
			if money_in_market:
				if high/buy_in_price >= 1.05:
					avail_cash = high * num_shares
					num_shares = 0
					money_in_market = False
					buy_in_price = 0

			else:
				if low/high_so_far <= 0.97:
					num_shares = avail_cash/low
					avail_cash = 0
					money_in_market = True
					buy_in_price = low

		balance = avail_cash + (num_shares * close)

	return balance

	

balance = run_buy_and_hold_algo(starting_cash, data)
#balance = zeus_algo(starting_cash, data)
print('The starting balance is: ' + str(starting_cash))
print('The ending balance is: ' + str(balance))



