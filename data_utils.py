
class DataUtils:
	"""
		A collection of useful functions for manipulating 
		the stock data.
	"""

	@staticmethod
	def get_rows(data, start_index=0, end_index=None):
		if not end_index:
			end_index = len(data)
		return data.iloc[start_index:end_index]

	@staticmethod
	def get_row_iterable(data, start_index=0, end_index=None):
		if not end_index:
			end_index = len(data)
		return data.iloc[start_index:end_index].iterrows()

	@staticmethod
	def get_low_from_row(row):
		return float(row['Low'])

	@staticmethod
	def get_high_from_row(row):
		return float(row['High'])	

	@staticmethod
	def get_close_from_row(row):
		return float(row['Close'])

	@staticmethod
	def get_date_from_row(row):
		return row['Date']