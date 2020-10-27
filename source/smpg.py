import numpy as np
from tools import read
import matplotlib.pyplot as plt


class smpgTools():

	def __init__(self, fst_yr, lst_yr, fst_cm, lst_cm, fst_dk, lst_dk, places_num):

		self.fst_yr = fst_yr
		self.lst_yr = lst_yr
		self.fst_cm = fst_cm
		self.lst_cm = lst_cm
		self.fst_dk = fst_dk
		self.lst_dk = lst_dk
		self.yrs = range(fst_yr, lst_yr)
		self.places_num = places_num
		self.dek_num = len(self.yrs) * 36
		self.clim_wind = range(fst_cm, lst_cm+1)

#============================================================
	def general_table(self, raw_data):

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
#============================================================
#============================================================
#============================================================
#============================================================
	def generate_report(self):
		pass
#============================================================

fst_yr, lst_yr, ID, raw_data = read('ejemplo1.csv')

places_num = len(ID)
SMPG = smpgTools(fst_yr, lst_yr, 1981, 2010, 1, 1, places_num)
a, b = SMPG.general_table(raw_data)
lta = SMPG.lt_average(a)

print(lta)








