import zipfile
import os
import csv
import sqlite3


def create_connection(db_file):
	""" create a database connection to a SQLite database """
	try:
	    conn = sqlite3.connect(db_file)
	    print(sqlite3.version)
	except Error as e:
	    print(e)

	return conn

def extract_file(path_to_data, file):
	print('Extracting ' + file)
	filepath = path_to_data + '/' + file
	with zipfile.ZipFile(filepath, 'r') as zip_ref:
		zip_ref.extractall(path_to_data)
		csv_file = file.replace('zip', 'csv')
		csv_filepath = path_to_data + '/' + csv_file
		print('The extracted file is ' + csv_file)
		return(csv_filepath)


	# ['SPY', '2019-06-21 16:15:00', 'SPY', '2021-12-17', '410.000', 'P', '0.0000', '0.0000', '0.0000', '0.0000', '0', '50', '114.7300', '10', '117.9800', '293.6400', '293.6600', '16', '1', '1', '114.0000', '1', '119.0000', '65', '1', '108.4100', '1', '124.0000', '4', '2', '114.0000', '2', '119.0000', '69', '2', '114.0000', '2', '119.0000', '5', '10', '114.7000', '10', '117.9800', '6', '10', '114.0000', '10', '118.9700', '7', '1', '114.0000', '1', '119.0000', '71', '20', '114.0000', '20', '119.0000', '9', '50', '114.7300', '50', '118.0000', '42', '10', '113.9100', '10', '118.8100', '11', '2', '114.0000', '2', '119.0000', '43', '20', '114.0000', '20', '119.0000', '47', '1', '114.0000', '1', '119.0000', '22', '20', '111.0200', '20', '121.0200', '60', '10', '114.7100', '10', '118.0000', '31', '20', '114.0000', '20', '119.0000']
	# ['underlying_symbol', 'quote_datetime', 'root', 'expiration', 'strike', 'option_type', 
	#'open', 'high', 'low', 'close', 'trade_volume', 'bid_size', 'bid', 'ask_size', 'ask', 
	# 'underlying_bid', 'underlying_ask', 'number_of_exchanges', '{exchange', 'bid_size', 
	# 'bid', 'ask_size', 'ask}[number_of_exchanges]']

def shape_data(filepath):
	print('Shaping data from csv')
	shaped_data = []

	# Defining row indices that will be extracted
	UNDERLYING_SYMBOL_INDEX = 0
	QUOTE_DATETIME_INDEX = 1
	EXPIRATION_INDEX = 3
	STRIKE_INDEX = 4
	OPTION_TYPE_INDEX = 5
	BID_INDEX = 12
	ASK_INDEX = 14
	UNDERLYING_BID_INDEX = 15
	UNDERLYING_ASK_INDEX = 16

	with open(filepath) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		first_row = True
		row_count = 0
		for row in csv_reader:
			if row_count != 0:
				new_tuple = (
					row[QUOTE_DATETIME_INDEX],
					row[EXPIRATION_INDEX],
					row[STRIKE_INDEX],
					row[OPTION_TYPE_INDEX],
					row[BID_INDEX],
					row[ASK_INDEX],
					row[UNDERLYING_BID_INDEX],
					row[UNDERLYING_ASK_INDEX]		
				)
				shaped_data.append(new_tuple)
			row_count += 1
	return [shaped_data, row_count - 1]

		# options_table_sql = """
	#         CREATE TABLE IF NOT EXISTS spy_options_data (
	#         quote_datetime text NOT NULL,
	#         expiration text NOT NULL,
	#         strike real NOT NULL,
	#         option_type text NOT NULL,
	#         bid real NOT NULL,
	#         ask real NOT NULL,
	#         underlying_bid real NOT NULL,
	#         underlying_ask real NOT NULL,
	#         PRIMARY KEY (quote_datetime, expiration, strike, option_type))
	#     """

# 	ows = [('2006-03-28', 'BUY', 'IBM', 1000, 45.00),
#         ('2006-04-05', 'BUY', 'MSOFT', 1000, 72.00),
#         ('2006-04-06', 'SELL', 'IBM', 500, 53.00)]
# c.executemany('insert into stocks values (?,?,?,?,?)', rows)
# connection.commit()

def insert_data_into_db(shaped_data, db_file):
	print('Inserting data into database')
	with create_connection(db_file) as conn:
		cur = conn.cursor()
		sql = ''' 
			INSERT INTO spy_options_data
			VALUES (?,?,?,?,?,?,?,?)
		'''
		cur.executemany(sql, shaped_data)
	

def delete_extracted_file(filepath):
	print('Deleting csv')
	os.remove(filepath)

def main():
	database_file = './options_data.db'
	total_rows_processed = 0

	# Getting directory this script is running in 
	current_path = os.path.dirname(os.path.abspath(__file__))

	# Path the zip files are in
	path_to_data = current_path + '/data'

	# For each file we 
	for file in os.listdir(path_to_data):
	    if file.endswith(".zip"):
	    	filepath = os.path.join(path_to_data, file)

	    	print('------------------------------------------------')
	    	extracted_file = extract_file(path_to_data, file)
	    	[shaped_data, rows_processed] = shape_data(extracted_file)
	    	insert_data_into_db(shaped_data, database_file)
	    	delete_extracted_file(extracted_file)
	    	print('Number of rows processed for this file: ' + str(rows_processed))
	    	total_rows_processed += rows_processed

	print('Data processing complete, total number of rows processed: ' + str(total_rows_processed))


main()
