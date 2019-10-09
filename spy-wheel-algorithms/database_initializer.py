"""
    This script takes care of creating the sqlite database to hold all the data
    for the spy wheel algorithms
"""

import sqlite3
from sqlite3 import Error
 
DATABASE_FILE = './spy_data.db'

def main(db_file):
    options_table_sql = """
        CREATE TABLE IF NOT EXISTS spy_options_data (
            quote_datetime text NOT NULL,
            expiration text NOT NULL,
            strike real NOT NULL,
            option_type text NOT NULL,
            bid real NOT NULL,
            ask real NOT NULL,
            underlying_bid real NOT NULL,
            underlying_ask real NOT NULL,
            PRIMARY KEY (quote_datetime, expiration, strike, option_type)
        )
    """
    stock_table_sql = """
        CREATE TABLE IF NOT EXISTS spy_stock_data (
            date text PRIMARY KEY,
            open real NOT NULL,
            high real NOT NULL,
            low real NOT NULL,
            close real NOT NULL
        )
    """
    conn = create_connection(db_file)

    # Creating options data table
    create_table(conn, options_table_sql)

    # Creating stock data table
    create_table(conn, stock_table_sql)
 
def create_connection(db_file):
	""" create a database connection to a SQLite database """
	try:
	    conn = sqlite3.connect(db_file)
	    print(sqlite3.version)
	except Error as e:
	    print(e)

	return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


 
if __name__ == '__main__':
	main(DATABASE_FILE)