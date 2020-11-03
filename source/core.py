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
		self.dlen = range(36) 
		self.clim_wind = range(fst_cm, lst_cm+1)
		self.deks = utils.dek_list()
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
			ensemble.append(dict(zip(self.yrs, loc)))

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
	def plotter(self, num, iD, LTA, actyr, ssn, acms, asts, cacms, ensb, ests):
		'''An iterable method designed to output a single 
		report

		:param num: figure number
		:param iD: Location/place name
		:param LTA: Long term avg. array for a location
		:param actyr: Actual year dekadals rainfall
		:param ssn: reference, season
		:param acms: Analog accumulations in a place 
		:param asts: Seasonal analog statistics
		:param cacms: Accumulations for current year
		:param ensb: Analog ensemble in a place
		:param ests: Analog ensemble statistics
		''' 
		# Config
		fig = plt.figure(num=num, tight_layout=True, figsize=(10, 6))
		gs = GridSpec(2, 3)

		# Gridspecs
		AX1 = fig.add_subplot(gs[0, :2])
		AX2 = fig.add_subplot(gs[1, 0])
		AX3 = fig.add_subplot(gs[1, 1])
		AX4 = fig.add_subplot(gs[:, 2])

		# Titles
		AX1.set_title('Average & current rainfall season: {}'.format(iD))
		AX2.set_title("Seasonal Accumulations")
		AX3.set_title("Ensemble")
		AX4.set_title("Summary Statistics")
		
		# x-labels
		AX1.set_xlabel("Dekads")
		AX2.set_xlabel("Dekads")
		AX3.set_xlabel("Dekads")

		# x-label ticks
		AX1.set_xticks(self.dlen)
		AX1.set_xticklabels(self.deks, rotation='vertical')

		# y-labels
		AX1.set_ylabel("Rainfall [mm]")
		AX2.set_ylabel("Accumulated Rainfall [mm]")
		AX3.set_ylabel("Accumulated Rainfall [mm]")

		# Variables
		ltm, std, thrd, sxth, mu, sgm, h, l = asts
		eltm, estd, ethrd, esxth, emu, esgm, eh, el = ests
		sx_axis = range(ssn)
		sx_end = sx_axis[-1]
		cx_axis = range(len(cacms))

		# AX1 plot
		AX1.plot(self.dlen, LTA, color='r', lw=5, label='LTA: {}-{}'.format(self.fst_cm, self.lst_cm))
		AX1.bar(range(13), actyr, color='b', label='Current year: {}'.format(self.lst_yr))
		AX1.legend()

		# AX2 plot
		for analogs in range(self.an_num): AX2.plot(sx_axis, acms[analogs])
		AX2.plot(sx_axis, ltm, color='r', lw=5, label='LTM')
		AX2.fill_between(sx_axis, h, l, color='lightblue', label='120-80%')
		AX2.plot(sx_end, thrd, marker='s', markersize=7, color='k', label='33rd pct')
		AX2.plot(sx_end, sxth, marker='s', markersize=7, color='k', label='67th pct')
		AX2.plot(sx_end, mu, marker='^', markersize=7, color='green', label='Avg+Std')
		AX2.plot(sx_end, sgm, marker='^', markersize=7, color='green', label='Avg-Std')
		AX2.plot(cx_axis, cacms, color='b', lw=5, label=self.lst_yr)

		# AX3 plot
		for analogs in range(self.an_num): AX3.plot(sx_axis, ensb[analogs])
		AX3.plot(sx_axis, eltm, '--', color='k', lw=2, label='ELTM')
		AX3.plot(sx_axis, ltm, color='r', lw=4, label='LTM')
		AX3.fill_between(sx_axis, h, l, color='lightblue', label='120-80%')
		AX3.plot(sx_end, thrd, marker='s', markersize=7, color='k', label='33rd pct')
		AX3.plot(sx_end, sxth, marker='s', markersize=7, color='k', label='67th pct')
		AX3.plot(sx_end, mu, marker='^', markersize=7, color='green', label='Avg+Std')
		AX3.plot(sx_end, sgm, marker='^', markersize=7, color='green', label='Avg-Std')
		AX3.plot(cx_axis, cacms, color='b', lw=4, label=self.lst_yr)
		AX3.plot(sx_end, ethrd, marker='s', markersize=7, color='blue', label='E_33rd pct')
		AX3.plot(sx_end, esxth, marker='s', markersize=7, color='blue', label='E_67th pct')
		AX3.plot(sx_end, emu, marker='^', markersize=7, color='orange', label='E_Avg+Std')
		AX3.plot(sx_end, esgm, marker='^', markersize=7, color='orange', label='E_Avg-Std')





		plt.show()
#=====================================================================
	def reports(self, _iD, _lta, _actyr, _acms, _asts, _cacms, _ensb, _ests):
		DICT = utils.spawn_deks()
		START = DICT[self.fst_dk]
		END = DICT[self.lst_dk]
		#LAST = self.yrs_len[-1]
		SEASON = len(range(START, END))
		if START < END:
			SEASON = len(range(START, END+1))
		else:
			a = len(range(START, 36))
			b = len(range(0, END+1))	
			SEASON = a + b	
		
		for place in range(self.places_num):
			iD = _iD[place]
			lta = _lta[place]
			yr = _actyr[place]
			acms = _acms[place]
			num = place + 1
			asts = _asts[place]
			cacms = _cacms[place]
			ensb = _ensb[place]
			ests = _ests[place]
			self.plotter(num, iD, lta, yr, SEASON, acms, asts, cacms, ensb, ests)


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
vector3, stats3 = SMPG.analog_ensemble(analogs, ensemble)
vector4, stats4 = SMPG.climatological_ensemble(ensemble)

ok = utils.outlook(stats2[1], vector4)


#angs = utils.export_analogs(ID, ranking)
#stats, percs = list(utils.stats(vector))
stats = utils.stats(vector)
#print(stats)
#print(percs)

#print(current_acms)
report = SMPG.reports(ID, lta, b, vector, stats2[0], current_acms, vector3, stats4[0]) 

'''
b = b[0]
lta = lta[0]
acms = vector[0]
SMPG.plotter(1, 'Carara', lta, b, 1, 1)
'''


