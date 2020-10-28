'''
Auxiliar functions to 
help smpgTools class
'''
import numpy as np
import pandas as pd
from scipy.stats import rankdata
#============================================================
def year_format(number):

	return int(number // 100)
#============================================================
def read(csv_file):

	# Read raw dataset as Pandas dataframe
	data = pd.read_csv(csv_file, header=None)

	# Choose first year
	fst_yr = year_format(data.loc[0][1])

	# Filter locations ID/names
	ID = list(data[0].loc[1:])

	# Choose last year and raw data for each place
	if data.loc[0].iloc[-1] == 'scenario':
		lst_yr = year_format(data.loc[0].iloc[-2])
		scenarios = list(data.iloc[1:,-1:])
		
		raw_data = []
		for i in range(len(ID)):
			location = list(data.loc[i+1][1:-1])
			raw_data.append(location)

		return fst_yr, lst_yr, ID, raw_data, scenarios

	else:
		lst_yr = year_format(data.loc[0].iloc[-1])
		raw_data = []
		for i in range(len(ID)):
			location = list(data.loc[i+1][1:])
			raw_data.append(location)

		return fst_yr, lst_yr, ID, raw_data
#============================================================
def spawn_deks():
	'''
	Returns a standard dictionary of dekads
	'''
	DEK = {'1-Jan': 0, '2-Jan': 1, '3-Jan': 2, '1-Feb': 3, 
		   '2-Feb': 4, '3-Feb': 5, '1-Mar': 6, '2-Mar': 7, 
		   '3-Mar': 0, '1-Apr': 9, '2-Apr': 10, '3-Apr': 11, 
		   '1-May': 12, '2-May': 13,'3-May': 14, '1-Jun': 15, 
		   '2-Jun': 16, '3-Jun': 17,'1-Jul': 18, '2-Jul': 19, 
		   '3-Jul': 20, '1-Aug': 21,'2-Aug': 22, '3-Aug': 23, 
		   '1-Sep': 24, '2-Sep': 25,'3-Sep': 26, '1-Oct': 27, 
		   '2-Oct': 28, '3-Oct': 29,'1-Nov': 30, '2-Nov': 31, 
		   '3-Nov': 32, '1-Dec': 33,'2-Dec': 34, '3-Dec': 35}
	return DEK
#============================================================
def sum_dekad_error(season_arr):
	pass
#============================================================
def sum_error_square(season_arr):
	pass
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
