"""
    This script retrieves historical stock data for the SPY etf and puts
    it into a sqlite database for more efficient use.  The script retrieves 
    the data using Tradier's API.
"""

import requests
import json
import sqlite3


def main():
    config_file = 'config.json'
    db_file = 'spy_data.db'

    config = get_config(config_file)
    data = get_data(config)
    shaped_data = shape_data(data)
    insert_data_into_db(shaped_data, db_file)

def get_config(config_file):
    # Getting config from json file
    with open(config_file) as json_file:
        config = json.load(json_file)
        return config

def get_data(config):
    # Making request to Tradier for the historical SPY data
    url = 'https://sandbox.tradier.com/v1/markets/history'
    response = requests.get(url,
        params={'symbol': 'SPY', 'interval': 'daily', 'start': '2019-01-01', 'end': '2019-09-13'},
        headers={'Authorization': 'Bearer ' + config['access_token'], 'Accept': 'application/json'}
    )
    data = response.json()
    return data['history']['day']

def shape_data(data):
    # Shapes the data to be inserted into the database.
    # Table structure is below:
    # 
    # CREATE TABLE IF NOT EXISTS spy_stock_data (
    #         date text PRIMARY KEY,
    #         open real NOT NULL,
    #         high real NOT NULL,
    #         low real NOT NULL,
    #         close real NOT NULL
    # )

    shaped_data = []
    for quote in data:
        new_tuple = (
            quote['date'],
            quote['open'],
            quote['high'],
            quote['low'],
            quote['close']
        )
        shaped_data.append(new_tuple)
    print(shaped_data)
    return shaped_data

def insert_data_into_db(shaped_data, db_file):
    # Inserts shaped data into the database
	print('Inserting data into database')
	with create_connection(db_file) as conn:
		cur = conn.cursor()
		sql = ''' 
			INSERT INTO spy_stock_data
			VALUES (?,?,?,?,?)
		'''
		cur.executemany(sql, shaped_data)

def create_connection(db_file):
    # Create a database connection to a SQLite database
	try:
	    conn = sqlite3.connect(db_file)
	    print(sqlite3.version)
	except Error as e:
	    print(e)

	return conn
    

main()