'''
Auxiliar functions to 
help smpgTools class
'''
import numpy as np
import pandas as pd
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
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
