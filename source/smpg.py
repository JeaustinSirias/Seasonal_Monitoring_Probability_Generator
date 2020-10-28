import numpy as np
from tools import read, spawn_deks
import matplotlib.pyplot as plt


class smpgTools():
	
	'''
	A class that contains all the necessary methods to
	build the SMPG.
	'''

	def __init__(self, fst_yr, lst_yr, fst_cm, lst_cm, fst_dk, lst_dk, places_num):

		self.fst_yr = fst_yr
		self.lst_yr = lst_yr
		self.fst_cm = fst_cm
		self.lst_cm = lst_cm
		self.fst_dk = fst_dk
		self.lst_dk = lst_dk
		self.yrs = range(fst_yr, lst_yr)
		self.yrs_len = range(len(self.yrs))
		self.places_num = places_num
		self.dek_num = len(self.yrs) * 36
		self.clim_wind = range(fst_cm, lst_cm+1)

#============================================================
	def general_table(self, raw_data):

		'''
		The main entry table. Classifies rainfall data by year
		using dekadals. :raw_data
		'''

		main_table = []
		current_yr_table = []

		for i in range(self.places_num):
			past = raw_data[i][0:self.dek_num]
			past = np.split(np.array(past), len(self.yrs))
			current = raw_data[i][self.dek_num:]
			main_table.append(past)
			current_yr_table.append(current)

		return main_table, current_yr_table
#============================================================
	def lt_average(self, main_table):

		lta_vect = []
		for i in range(self.places_num):
			lta = []
			place = np.array(main_table[i]).transpose()
			for j in range(36):
				row = place[j][0:len(self.clim_wind)]
				row = np.mean(row)
				lta.append(row)

			lta_vect.append(lta)

		return lta_vect
#============================================================
	def seasonal_table(self, main_table, current_yr_table):

		boolean_table = []
		seasonal_table = []
		DICT = spawn_deks()
		START = DICT[self.fst_dk]
		END = DICT[self.lst_dk]
		LAST = self.yrs_len[-1]
		SEASON = len(range(START, END))

		if START < END:
			SEASON = len(range(START, END+1))
		else:
			a = len(range(START, 36))
			b = len(range(0, END+1))	
			SEASON = a + b	

		# STEP 1: SEASONAL TABLE:
		for i in range(self.places_num):
			loc = []
			loc_s = []
			for j in self.yrs_len:
				if j < LAST:
					yr = main_table[i][j][START:] 
					add = main_table[i][j+1][:START]
					yr = np.append(yr, add)
					ssn = yr[:SEASON]
					loc.append(yr)
					loc_s.append(ssn)
				else:
					yr = main_table[i][j][START:] 
					add = current_yr_table[i][:START]
					yr = np.append(yr, add)

					if len(yr) < 36:
						OFFSET = 36 - len(yr)
						arr = np.array([0] * OFFSET)
						yr = np.append(yr, arr)

					ssn = yr[:SEASON]
					loc.append(yr)
					loc_s.append(ssn)

			boolean_table.append(loc)
			seasonal_table.append(loc_s)

		return seasonal_table, boolean_table
#============================================================
	def seasonal_accummulations(self, seasonal_table, curr):

		seasonal_accummulations = []
		current_accummulations = []
		season = range(len(seasonal_table[0][0]))
		places, deks = np.array(curr).shape

		# PAST YEARS ACCUMMULATIONS
		for place in range(self.places_num):
			yr = []
			for year in self.yrs_len:
				accum = 0
				ssn =[]
				for dek in season:
					accum += seasonal_table[place][year][dek]
					ssn.append(accum)
				yr.append(ssn)
			seasonal_accummulations.append(yr)

		# CURRENT YEAR ACCUMULATIONS
		for place in range(places):
			accum = 0
			arr = []
			for dek in range(deks):
				accum += curr[place][dek]
				arr.append(accum)
			current_accummulations.append(arr)

		return seasonal_accummulations, current_accummulations
#============================================================

#============================================================
#============================================================
	def generate_report(self):
		pass
#============================================================

fst_yr, lst_yr, ID, raw_data = read('ejemplo1.csv')

places_num = len(ID)
SMPG = smpgTools(fst_yr, lst_yr, 1981, 2010, '1-Feb', '3-May', places_num)
a, b = SMPG.general_table(raw_data)
lta = SMPG.lt_average(a)
s_table, b_table = SMPG.seasonal_table(a, b)
season_acms, current_acms = SMPG.seasonal_accummulations(s_table, b)

print(current_acms)






