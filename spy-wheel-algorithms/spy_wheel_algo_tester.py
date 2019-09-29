# Importing algorithms
from zeus import Zeus



def initialize_algorithms(starting_cash):
	# Instantiating the algorithms



	algorithm_objects = [


	]

	return algorithm_objects



def main(starting_cash, starting_date, end_date):
	algorithm_objects = initialize_algorithms(starting_cash)

	# Going day by day and running each algorithm
	for algo_obj in algorithm_objects:
		algo_obj.run(starting_date, end_date, db_conn)


	# Printing out the results
	for algo in algorithm_objects:
		algo.print_out()




STARTING_CASH = 500000
START_DATE = '2019-01-01'
END_DATE = '2019-09-29'

# main(STARTING_CASH, START_DATE, END_DATE)
test = Zeus(100)
test.print_out()
	

