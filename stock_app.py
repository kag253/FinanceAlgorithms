#!/usr/local/bin/python3
import json
import requests

# Third-party library: https://github.com/AndrewRPorter/yahoo-historical
from yahoo_historical import Fetcher

from data_utils import DataUtils
from market_position import MarketPosition

# Importing the financial algorithms
from buy_and_hold import BuyAndHold
from buy_every_day_and_hold import BuyEveryDayAndHold
from zeus import Zeus



def get_data_from_api(symbol, start_date, end_date):
	fetcher = Fetcher(symbol, start_date, end_date)
	data = fetcher.getHistorical()
	return data
	

#fetcher = Fetcher('AAPL', [1990, 1, 1], [2017, 9, 21])
data = get_data_from_api('AAPL', [1980, 9, 1], [2017, 10, 1])

# Inputs
stocks_to_test = ['MSFT', 'AAPL', 'TSLA', 'NFLX', 'JNJ', 'KO', 'FB']
starting_cash = 5000
monthly_cash_infusion = 1000
total_cash_used = starting_cash 


# Creating the algo objects (and running them the first day)
algo_objects = {}
first_day = DataUtils.get_rows(data, 0, 1)[0]
algo_objects['buy_and_hold'] = BuyAndHold(first_day, starting_cash)
algo_objects['buy_every_day_and_hold'] = BuyEveryDayAndHold(first_day, starting_cash)
total_cash_used += monthly_cash_infusion
# for s in range(1, 16):
# 	for b in range(1, 16):
# 		sell_percent = s / 100
# 		buy_percent = b / 100
# 		name = '{algo_name}_{sell_percent}_{buy_percent}'.format(
# 			algo_name='zeus', 
# 			sell_percent=sell_percent, 
# 			buy_percent=buy_percent
# 		)
# 		algo_objects[name] = Zeus(first_day, starting_cash, sell_percent, buy_percent)


# Running the algos
counter = 0
num_rows = len(data)
for index, row in DataUtils.get_row_iterable(data, 1, num_rows - 1):
	if row['High'] == 'null':
		continue

	if counter == 30:
		for name, algo_obj in algo_objects.items():
			algo_obj.run(row, monthly_cash_infusion)
		counter = 0
		total_cash_used += monthly_cash_infusion
	else:
		for name, algo_obj in algo_objects.items():
			algo_obj.run(row, 0)
		counter += 1


# Selling out the algos
last_day = DataUtils.get_rows(data, num_rows - 1, num_rows)[0]
results = []
for name, algo_obj in algo_objects.items():
	results.append([algo_obj.run(row, 0, True), name])
results.sort()



print('The starting cash amount is: '+str(starting_cash))
print('The monthly cash infusion amount is: '+str(monthly_cash_infusion))
print('The total cash amount used is: '+str(total_cash_used))
print()
print('Results')
print('-'*20)
for row in results:
	print(row[1] + ': ' + str(row[0]))







