"""
	This script imports all the spy option data from the zip files it
	came in, into a sqlite database for more efficient use.
"""

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

def shape_data(filepath):
	print('Shaping data from csv')
	shaped_data = []

	# Defining row indices that will be extracted
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
	database_file = './spy_data.db'
	total_rows_processed = 0

	# Getting directory this script is running in 
	current_path = os.path.dirname(os.path.abspath(__file__))

	# Path the zip files are in
	path_to_data = current_path + '/data'

	# For each file we 
	for file in os.listdir(path_to_data):
	    if file.endswith(".zip"):
	    	print('------------------------------------------------')
	    	extracted_file = extract_file(path_to_data, file)
	    	[shaped_data, rows_processed] = shape_data(extracted_file)
	    	insert_data_into_db(shaped_data, database_file)
	    	delete_extracted_file(extracted_file)
	    	print('Number of rows processed for this file: ' + str(rows_processed))
	    	total_rows_processed += rows_processed

	print('Data processing complete, total number of rows processed: ' + str(total_rows_processed))


main()
