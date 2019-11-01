# Importing algorithms
from zeus import Zeus
import sqlite3

def create_connection(db_file):
	""" create a database connection to a SQLite database """
	try:
	    conn = sqlite3.connect(db_file)
	    print(sqlite3.version)
	    return conn
	except Exception as e:
	    print(e)
	    return None


def initialize_algorithms(starting_cash, starting_date, end_date, db_conn):
	# Instantiating the algorithms
	algorithm_objects = [
		Zeus(starting_cash, starting_date, end_date, db_conn)
	]

	return algorithm_objects



def main(starting_cash, starting_date, end_date, db_file):
	# Creating the db connection for the algorithms to use
	db_conn = create_connection(db_file)


	algorithm_objects = initialize_algorithms(starting_cash, starting_date, end_date, db_conn)

	# Going day by day and running each algorithm
	for algo_obj in algorithm_objects:
		algo_obj.run()


	# Printing out the results
	# for algo_obj in algorithm_objects:
	# 	algo_obj.print_out()



DB_FILE = 'spy_data.db'
STARTING_CASH = 30000
START_DATE = '2019-01-02'
END_DATE = '2019-09-14'

main(STARTING_CASH, START_DATE, END_DATE, DB_FILE)
# test = Zeus(100)
# test.print_out()
	

