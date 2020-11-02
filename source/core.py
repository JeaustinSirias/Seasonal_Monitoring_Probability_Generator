import numpy 
import utils 
from scipy.stats import rankdata
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

class smpgTool():
	'''A class that contains all the necessary methods to
	build the SMPG.
	'''
	def __init__(
					self, 
					fst_yr, 
					lst_yr, 
					fst_cm, 
					lst_cm, 
					fst_dk, 
					lst_dk, 
					places_num,
					analogs_num
				):

		self.fst_yr = fst_yr
		self.lst_yr = lst_yr
		self.fst_cm = fst_cm
		self.lst_cm = lst_cm
		self.fst_dk = fst_dk
		self.lst_dk = lst_dk
		self.an_num = analogs_num
		self.yrs = range(fst_yr, lst_yr)
		self.yrs_len = range(len(self.yrs))
		self.places_num = places_num
		self.dek_num = len(self.yrs) * 36
		self.clim_wind = range(fst_cm, lst_cm+1)
#=====================================================================
	def general_table(self, raw_data):
		'''The main entry table. Classifies rainfall data by 
		location and sets up a 2D grid map as [dekad, year]
		
		:param raw_data: Contains the raw CSV data format
		:return main_table: The main SMPG table
		:return current_yr_table: Current year array
		'''

		main_table = []
		current_yr_table = []

		for i in range(self.places_num):
			past = raw_data[i][0:self.dek_num]
			past = numpy.split(numpy.array(past), len(self.yrs))
			current = raw_data[i][self.dek_num:]
			main_table.append(past)
			current_yr_table.append(current)

		return main_table, current_yr_table
#=====================================================================
	def LTM(self, main_table):
		'''Computes long-term average rows for each of the
		36 dekadals in every location detected in the 
		input dataset
		:param main_table: The SMPG general table 
		'''

		lta_vect = []
		for i in range(self.places_num):
			lta = []
			place = numpy.array(main_table[i]).transpose()
			for j in range(36):
				row = place[j][0:len(self.clim_wind)]
				row = numpy.mean(row)
				lta.append(row)

			lta_vect.append(lta)

		return lta_vect
#=====================================================================
	def seasonal_table(self, main_table, current_yr_table):
		'''Computes the general table and trims the chosen 
		season by the user, but also it refills each 
		missing dekad with the next elements in []

		:param main_table: The SMPG general table
		:param current_yr_table:
		'''

		boolean_table = []
		seasonal_table = []
		present_table  = []
		DICT = utils.spawn_deks()
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
			current_ssn = current_yr_table[i][START:]
			present_table.append(current_ssn)
			for j in self.yrs_len:
				if j < LAST:
					yr = main_table[i][j][START:] 
					add = main_table[i][j+1][:START]
					yr = numpy.append(yr, add)
					ssn = yr[:SEASON]
					loc.append(yr)
					loc_s.append(ssn)
				else:
					yr = main_table[i][j][START:] 
					add = current_yr_table[i][:START]
					yr = numpy.append(yr, add)

					if len(yr) < 36:
						OFFSET = 36 - len(yr)
						arr = numpy.array([0] * OFFSET)
						yr = numpy.append(yr, arr)

					ssn = yr[:SEASON]
					loc.append(yr)
					loc_s.append(ssn)

			boolean_table.append(loc)
			seasonal_table.append(loc_s)

		return seasonal_table, boolean_table, present_table
#=====================================================================
	def seasonal_accummulations(self, seasonal_table, curr):
		'''Computes the accummulations over each year column
		only in the chosen season. It does it for all past
		years an for the current year (until it's possible)

		:param seasonal_table:
		:param curr:
		:return seasonal_accummulations:
		:return current_accummulations:
		:return Dict:
		'''

		Dict = []
		seasonal_accummulations = []
		current_accummulations = []
		season = range(len(seasonal_table[0][0]))
		places, deks = numpy.array(curr).shape

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
			Dict.append(dict(zip(self.yrs, yr)))

		# CURRENT YEAR ACCUMULATIONS
		for place in range(places):
			accum = 0
			arr = []
			for dek in range(deks):
				accum += curr[place][dek]
				arr.append(accum)
			current_accummulations.append(arr)

		return seasonal_accummulations, current_accummulations, Dict
#=====================================================================
	def seasonal_ensemble(self, seasonal_table, present_accum):

		dim2 = len(present_accum[0])
		dim3 = len(seasonal_table[0][0])
		bias = range(dim2, dim3)
		ensemble = []

		for place in range(self.places_num):
			vector = present_accum[place]
			loc = []
			for year in self.yrs_len:
				tail = []
				ADD = seasonal_table[place][year]
				VALUE = vector[-1]
				for dek in bias:
					VALUE += ADD[dek]
					tail.append(VALUE)
				loc.append(vector + tail)
			ensemble.append(loc)

		return ensemble
#=====================================================================
	def compute_analogs(self, SSE_ranking, SDE_ranking):

		# Ranking adittions
		ranking = []
		ord_dict = []
		for place in range(self.places_num):

			R1 = SSE_ranking[place]
			R2 = SDE_ranking[place]
			rank = [R1[i] + R2[i] for i in self.yrs_len]
			rank = rankdata(rank, method='dense')
			ord_rank = rankdata(rank, method='ordinal')
			ord_dict.append(dict(zip(ord_rank, self.yrs)))
			dictionary = defaultdict(list)
			carrier = [(self.yrs[i], rank[i]) for i in self.yrs_len]

			for year, key in carrier:
				dictionary[key].append(year)

			ranking.append(dict(dictionary))

		# Getting analog years lists
		analogs = []
		for place in range(self.places_num):
			an = [ord_dict[place][i+1] for i in range(self.an_num)]
			analogs.append(an)

		return ranking, analogs
#=====================================================================
	def analog_accumulation(self, analogs, accum_dict):
		'''
		Computes seasonal accumulations, but considering
		only the analog years amount chosen by the user.
		'''
		
		vector = []
		for place in range(self.places_num):
			List = analogs[place]
			v = [accum_dict[place][year] for year in List]
			vector.append(v)

		stats = utils.stats(vector)

		return vector, stats
#=====================================================================
	def climatological_accumulation(self, accum_dict):
		'''
		Computes seasonal accumulations, but considering
		the climatological window chosen by user.
		'''
		vector = []
		for place in range(self.places_num):
			v = [accum_dict[place][year] for year in self.clim_wind]
			vector.append(v)

		stats = utils.stats(vector)

		return vector, stats
#=====================================================================
	def analog_ensemble(self, analogs, ensemble):
		'''
		Computes the ensemble, but considering only 
		the analog years amount chosen by the user.
		'''
		vector = []
		for place in range(self.places_num):
			List = analogs[place]
			v = [ensemble[place][year] for year in List]
			vector.append(v)

		stats = utils.stats(vector)

		return vector, stats
#=====================================================================
	def climatological_ensemble(self, ensemble):

		vector = []
		for place in range(self.places_num):
			v = [ensemble[place][year] for year in self.clim_wind]
			vector.append(v)

		stats = utils.stats(vector)

		return vector, stats
#=====================================================================
#=====================================================================
	def report(self):
		return
#=====================================================================
fst_yr, lst_yr, ID, raw_data = utils.read('/home/jussc_/Desktop/Seasonal_Monitoring_Probability_Generator/data/ejemplo1.csv')

places_num = len(ID)
SMPG = smpgTool(fst_yr, lst_yr, 1981, 2010, '1-Feb', '3-May', places_num, 39)
a, b = SMPG.general_table(raw_data)
lta = SMPG.LTM(a)
s_table, b_table, p_table = SMPG.seasonal_table(a, b)
season_acms, current_acms, Dict = SMPG.seasonal_accummulations(s_table, p_table)
R1 = utils.SDE(s_table, p_table)
R2 = utils.SSE(season_acms, current_acms)
ranking, analogs = SMPG.compute_analogs(R1, R2)
ensemble = SMPG.seasonal_ensemble(s_table, current_acms)
vector, stats = SMPG.analog_accumulation(analogs, Dict)
vector2, stats2 = SMPG.climatological_accumulation(Dict)

angs = utils.export_analogs(ID, ranking)
stats = utils.stats(vector)
#print(stats)

