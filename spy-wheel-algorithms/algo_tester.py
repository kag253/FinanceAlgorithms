# Importing algorithms




def get_the_days_data(date):
	pass


def initialize_algorithms(starting_cash):
	# Instantiating the algorithms



	algorithm_objects = []

	return algorithm_objects



def main(starting_cash, starting_date, end_date):


	algorithm_objects = initialize_algorithms(starting_cash)
	current_date = starting_date

	# Going day by day and running each algorithm
	while current_date < end_date:
		data = get_the_days_data(current_date)
		for algo in algorithm_objects:
			algo.run(data)

		current_date += 1


	# Printing out the results
	for algo in algorithm_objects:
		algo.print_out()

	

