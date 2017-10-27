#!/usr/local/bin/python3
import json
import requests

# Third-party library: https://github.com/AndrewRPorter/yahoo-historical
from yahoo_historical import Fetcher

from data_utils import DataUtils
from market_position import MarketPosition

# Importing the financial algorithms
from buy_and_hold import BuyAndHold
from zeus import Zeus



def get_data_from_api(symbol, start_date, end_date):
	fetcher = Fetcher(symbol, start_date, end_date)
	data = fetcher.getHistorical()
	return data
	

#fetcher = Fetcher('AAPL', [1990, 1, 1], [2017, 9, 21])
data = get_data_from_api('MSFT', [2015, 1, 1], [2017, 9, 21])


# Inputs
stocks_to_test = ['MSFT', 'AAPL', 'TSLA', 'NFLX', 'JNJ', 'KO', 'FB']
starting_cash = 20000
monthly_cash_infusion = 1000


# Creating the algo objects (and running them the first day)
first_day = DataUtils.get_rows(data, 0, 1)[0]
buy_and_hold_algo = BuyAndHold(first_day, starting_cash)
zeus_algo = Zeus(first_day, starting_cash)


# Running the algos
counter = 0
num_rows = len(data)
for index, row in DataUtils.get_row_iterable(data, 1, num_rows - 1):
	# def run(self, data_row, cash_infusion, sell_out=False):
	if counter == 30:
		buy_and_hold_algo.run(row, monthly_cash_infusion)
		zeus_algo.run(row, monthly_cash_infusion)
		counter = 0
	else:
		buy_and_hold_algo.run(row, 0)
		zeus_algo.run(row, 0)
		counter += 1


# Selling out the algos
last_day = DataUtils.get_rows(data, num_rows - 1, num_rows)[0]
buy_and_hold_results = buy_and_hold_algo.run(last_day, 0, True)
zeus_results = zeus_algo.run(last_day, 0, True)



	
# Buys in the beginning, sells whenever 5% up AND long term tax rate eligible. 
# Re-buys when 3% down from 30 day moving high.
def zeus_hold_1_year(starting_cash, data):
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
				if market_position.long_term_tax_rate_eligible(date) and (high / market_position.buy_price) >= sell_percent: 
					balance = market_position.sell(date, high)
					market_position = None
			else: 
				if (low / high_so_far) <= buy_percent:
					market_position = MarketPosition(date, low, balance)
					

	return balance

#buy_and_hold_results = buy_and_hold(starting_cash, data)
#zeus_results = zeus(starting_cash, data)
zeus_hold_1_year_results = zeus_hold_1_year(starting_cash, data)


print('The starting cash amount is: '+str(starting_cash))
print()
print('Results')
print('-'*20)
print('buy_and_hold: \t\t' + str(buy_and_hold_results))
print('zeus: \t\t\t' + str(zeus_results))
print('zeus_hold_1_year: \t' + str(zeus_hold_1_year_results))





