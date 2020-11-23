# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 Jeaustin Sirias
#
import numpy 
import matplotlib.pyplot as plt
from .utils import season, Stats, dek_list, prob
from scipy.stats import rankdata
from collections import defaultdict
from matplotlib.gridspec import GridSpec

class smpgTool():
	'''A class that contains all the necessary methods to
	build the SMPG.
	'''
	def __init__(self, fst_yr, lst_yr, fst_cm, lst_cm, fst_dk, 
				 lst_dk, scn, places_num, analogs_num, savefile,
				 showfile, fct):

		self.fst_yr = fst_yr
		self.lst_yr = lst_yr
		self.fst_cm = fst_cm
		self.lst_cm = lst_cm
		self.fst_dk = fst_dk
		self.lst_dk = lst_dk
		self.scenario = scn
		self.an_num = analogs_num
		self.yrs = range(fst_yr, lst_yr)
		self.SEASON, self.START = season(fst_dk, lst_dk)
		self.yrs_len = range(len(self.yrs))
		self.places_num = places_num
		self.dek_num = len(self.yrs) * 36
		self.dlen = range(36) 
		self.clim_wind = range(fst_cm, lst_cm+1)
		self.deks = dek_list()
		self.savefile = savefile
		self.showfile = showfile
		self.forecast = fct
		self.actual = []
		self.actualacm = []
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
			if self.forecast:
				self.actual.append(current)
				current = current[:-1]
			main_table.append(past)
			current_yr_table.append(current)

		return main_table, current_yr_table
#=====================================================================
	def Average(self, main_table):
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
		#SEASON, START = utils.season(self.fst_dk, self.lst_dk)

		# STEP 1: SEASONAL TABLE:
		for i in range(self.places_num):
			loc = []
			loc_s = []
			current_ssn = current_yr_table[i][self.START:]
			present_table.append(current_ssn)
			for j in self.yrs_len:
				if j < self.yrs_len[-1]:
					yr = main_table[i][j][self.START:] 
					add = main_table[i][j+1][:self.START]
					yr = numpy.append(yr, add)
					ssn = yr[:self.SEASON]
					loc.append(yr)
					loc_s.append(ssn)
				else:
					yr = main_table[i][j][self.START:] 
					add = current_yr_table[i][:self.START]
					yr = numpy.append(yr, add)

					if len(yr) < 36:
						OFFSET = 36 - len(yr)
						arr = numpy.array([0] * OFFSET)
						yr = numpy.append(yr, arr)

					ssn = yr[:self.SEASON]
					loc.append(yr)
					loc_s.append(ssn)

			boolean_table.append(loc)
			seasonal_table.append(loc_s)

		return seasonal_table, present_table
#=====================================================================
	def seasonal_accummulations(self, seasonal_table, curr):
		'''Computes the accummulations over each year column
		only in the chosen season. It does it for all past
		years an for the current year (until it's possible)

		:param seasonal_table:
		:param curr:
		:return seasonal_accumulations:
		:return current_accumulations:
		:return Dict:
		'''
		Dict = []
		seasonal_accumulations = []
		current_accumulations = []
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
			seasonal_accumulations.append(yr)
			Dict.append(dict(zip(self.yrs, yr)))

		# CURRENT YEAR ACCUMULATIONS
		for place in range(places):
			accum = 0
			arr = []
			for dek in range(deks):
				accum += curr[place][dek]
				arr.append(accum)
			current_accumulations.append(arr)

		if self.forecast:
			for place in range(places):
				caccum = 0
				arr = []
				season = self.actual[place][self.START:]
				for fdek in range(deks+1):
					caccum += season[fdek]
					arr.append(caccum)
				self.actualacm.append(arr)

		return seasonal_accumulations, current_accumulations, Dict
#=====================================================================
	def seasonal_ensemble(self, seasonal_table, present_accum):
		'''
		:param:
		:param:
		:return:
		'''

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

		# Getting an analog years list
		analogs = []
		for place in range(self.places_num):
			an = [ord_dict[place][i+1] for i in range(self.an_num)]
			analogs.append(an)

		return ranking, analogs
#=====================================================================
	def analog_accumulation(self, analogs, accum_dict):
		'''Computes seasonal accumulations, but considering
		only the analog years amount chosen by the user.

		:param:
		:param:
		:return:
		'''
		vector = []
		for place in range(self.places_num):
			List = analogs[place]
			v = [accum_dict[place][year] for year in List]
			vector.append(v)

		stats, percs = Stats(vector, extrapercs=True)
		return vector, stats, percs
#=====================================================================
	def climatological_accumulation(self, accum_dict):
		'''Computes seasonal accumulations, but considering
		the climatological window chosen by user.

		:param:
		:return:
		'''
		vector = []
		for place in range(self.places_num):
			v = [accum_dict[place][year] for year in self.clim_wind]
			vector.append(v)
		stats, percs = Stats(vector, extrapercs=True)

		return stats, percs
#=====================================================================
	def scenario_analysis(self, values, ensemble):
		'''A method to compute the analysis for custom
		scenarios according to input rainfall values for
		each place from the dataset.

		:param values: a vector with custom rainfall values
		:param ensemble: the ensemble array (analog or climatological)
		:return: a vector of tuples with the HI and LO prob of being
		'''
		# Initiates the statistical vector
		stats = []
		size = len(ensemble[0])
		# Getting the statistic for the custom scenarios
		for place in range(self.places_num):
			row = numpy.array(ensemble[place]).transpose()[-1]
			value = values[place]
			HI, LO = 0, 0
			if value == -1:
				stats.append((None, None))
				continue
			for year in row:
				if year >= value:
					HI += 1
				else:
					LO += 1
			stats.append((prob(HI, size), prob(LO, size)))
	
		return stats
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

		stats = Stats(vector)
		return vector, stats
#=====================================================================
	def climatological_ensemble(self, ensemble):

		vector = []
		for place in range(self.places_num):
			v = [ensemble[place][year] for year in self.clim_wind]
			vector.append(v)

		stats = Stats(vector)
		return vector, stats
#=====================================================================
	def plotter(self, deks, num, iD, LTA, actyr, ssn, acms, asts, 
				cacms, ensb, ests, angs, aok, eok, aasts, cests,
				saltm, celtm, anlist, ascn, cscn, dirpath):
		'''An iterable method designed to output a single 
		report.

		:param deks: An array with the seasonal dekads
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
		:param angs: analog years ranking dictionary
		:param aok: outlook stats from analog years
		:param eok: outlook stats form climatology
		:param aasts: seasonal stats from analog years
		:param cests: ensemble stats from climatology
		:param saltm: seasonal LTM statistics
		:param celtm: climatological LTM statistics
		:param anlist: analog years list (ordinally ranked)
		:param ascn: analog scenario statistic
		:param cscn: climatological scenario statistic
		:param Dir: Directory where the report will be saved
		''' 
		# Frequently used variables
		col = 'Analog years', 'Climatology'
		altm, astd, athrd, asxth, amu, asgm, ah, al, aavg, amed = aasts
		ltm, std, thrd, sxth, mu, sgm, h, l, avg, med = asts
		eltm, estd, ethrd, esxth, emu, esgm, eh, el, eavg, emed = ests
		cltm, cstd, cthrd, csxth, cmu, csgm, ch, cl, cavg, cmed = cests
		atotal, aslta, altapct, aepct = saltm
		etotal, cslta, cltapct, cepct = celtm
		AA, AN, AB = aok
		CA, CN, CB = eok
		sx_axis = range(ssn)
		sx_end = sx_axis[-1]
		cx_axis = range(len(cacms))
		ac_axis = range(len(actyr))
		empty = [[None]]
		hdr = ['darkgray']
		k = 0.025

		# Config
		fig = plt.figure(
			num=num, 
			tight_layout=True, 
			figsize=(16, 9), 
			clear=True
			)
		fig.canvas.set_window_title('Code: {}'.format(iD))
		gs = GridSpec(2, 3)

		# Gridspecs
		AX1 = fig.add_subplot(gs[0, :2])
		AX2 = fig.add_subplot(gs[1, 0])
		AX3 = fig.add_subplot(gs[1, 1])
		AX4 = fig.add_subplot(gs[:, 2])
	
		# Titles
		AX1.set_title('Current rainfall status for {}'.format(iD))
		AX2.set_title("Seasonal Accumulations")
		AX3.set_title("Ensemble")
		AX4.set_title("Summary Statistics")
		
		# x-labels
		AX1.set_xlabel('Dekads')
		AX2.set_xlabel('Season')
		AX3.set_xlabel('Season')

		# y-labels
		AX1.set_ylabel("Rainfall [mm]")
		AX2.set_ylabel("Accumulated Rainfall [mm]")
		AX3.set_ylabel("Accumulated Rainfall [mm]")

		# Grids
		AX1.grid()
		AX2.grid()
		AX3.grid()

		# x-label ticks
		AX1.set_xticks(self.dlen)
		AX1.set_xticklabels(self.deks, rotation='vertical')
		AX2.set_xticks(sx_axis)
		AX2.set_xticklabels(deks, rotation='vertical')
		AX3.set_xticks(sx_axis)
		AX3.set_xticklabels(deks, rotation='vertical')

		# AX1 plot
		AX1.plot(
			self.dlen, 
			LTA, 
			color='r', 
			lw=5, 
			label='Climatological LTA: {}-{}'.format(self.fst_cm, self.lst_cm)
		)
		if self.forecast: 
			AX1.bar(
				range(len(actyr)+1), 
				self.actual[num], 
				color='m', 
				label='Forecasted dekad'
			)
		AX1.bar(
			ac_axis, 
			actyr, 
			color='b', 
			label='Current year rainfall status: {}'.format(self.lst_yr)
		)
	
		# AX2 plot
		if self.an_num > 5:
			for analogs in range(self.an_num): 
				AX2.plot(sx_axis, acms[analogs])
		else:
			for analogs in range(self.an_num):
				AX2.plot(sx_axis, acms[analogs], label = anlist[analogs])
		
		AX2.plot(sx_axis, ltm, color='r', lw=5, label='LTM')
		AX2.fill_between(
			sx_axis, 
			h, 
			l, 
			color='lightblue', 
			label='120-80%'
		)
		AX2.plot(
			sx_end, 
			thrd, 
			marker='s', 
			markersize=7, 
			color='k', 
			label='33rd pct'
		)
		AX2.plot(
			sx_end, 
			sxth, 
			marker='s', 
			markersize=7, 
			color='k', 
			label='67th pct'
		)
		AX2.plot(
			sx_end, 
			mu, 
			marker='^', 
			markersize=7, 
			color='green', 
			label='Avg+Std'
		)
		AX2.plot(
			sx_end, 
			sgm, 
			marker='^', 
			markersize=7, 
			color='green', 
			label='Avg-Std'
		)
		if self.forecast: 
			AX2.plot(
				range(len(cacms)+1), 
				self.actualacm[num], 
				color='m', 
				lw=5, 
				label='Forecast'
			)
		AX2.plot(
			cx_axis, 
			cacms, 
			color='b', 
			lw=5, 
			label=self.lst_yr
		)
	
		# AX3 plot
		for analogs in range(self.an_num): AX3.plot(sx_axis, ensb[analogs])
		AX3.plot(
			sx_axis, 
			ltm, 
			color='r', 
			lw=4, 
			label='LTM'
		)
		AX3.plot(
			sx_axis, 
			eltm, 
			'--', 
			color='k', 
			lw=2.5, 
			label=
			'ELTM'
		)
		AX3.fill_between(
			sx_axis, 
			h, 
			l, 
			color='lightblue', 
			label='120-80%'
		)
		AX3.plot(
			sx_end, 
			thrd, 
			marker='s', 
			markersize=7, 
			color='k', 
			label='33rd pct'
		)
		AX3.plot(
			sx_end, 
			sxth, 
			marker='s', 
			markersize=7, 
			color='k', 
			label='67th pct'
		)
		AX3.plot(
			sx_end, 
			mu, 
			marker='^', 
			markersize=7, 
			color='green', 
			label='Avg+Std'
		)
		AX3.plot(
			sx_end, 
			sgm, 
			marker='^', 
			markersize=7, 
			color='green', 
			label='Avg-Std'
		)
		AX3.plot(
			cx_axis, 
			cacms, 
			color='b', 
			lw=4, 
			label=self.lst_yr
		)
		AX3.plot(
			sx_end, 
			ethrd, 
			marker='s', 
			markersize=7, 
			color='blue', 
			label='E_33rd pct'
		)
		AX3.plot(
			sx_end, 
			esxth, 
			marker='s', 
			markersize=7, 
			color='blue', 
			label='E_67th pct'
		)
		AX3.plot(
			sx_end, 
			emu, 
			marker='^', 
			markersize=7, 
			color='orange', 
			label='E_Avg+Std'
		)
		AX3.plot(
			sx_end, 
			esgm, 
			marker='^', 
			markersize=7, 
			color='orange', 
			label='E_Avg-Std'
		)

		# Legends
		AX1.legend()
		AX2.legend(
			loc='upper center', 
			bbox_to_anchor=(0.5, -0.35), 
			shadow=True, 
			ncol=4, 
			fontsize=8
		)
		AX3.legend(
			loc='upper center', 
			bbox_to_anchor=(0.5, -0.35), 
			shadow=True, 
			ncol=4, 
			fontsize=8
		)

		# AX4 -Tables - Headers
		AX4.axis('off')
		AX4.table(
			cellText=empty, 
			colLabels=['Seasonal Analysis'], 
			bbox=[0.2, 0.68-k, 0.7, 0.12 ], 
			colColours=hdr
		)
		AX4.table(
			cellText=empty, 
			colLabels=['Assessment at current dekad'], 
			bbox=[0.2, 0.46-k, 0.7, 0.12 ], 
			colColours=hdr
		)
		AX4.table(
			cellText=empty, 
			colLabels=['Projection to the end of the season'], 
			bbox=[0.2, 0.24-k, 0.7, 0.12], 
			colColours=hdr
		)
		AX4.table(
			cellText=empty, 
			colLabels=['Probability at the end of season'], 
			bbox=[0.2, -0.13-k, 0.7, 0.12 ], 
			colColours=hdr
		)
		#if not ascn is None:
		if ascn != (None, None):
		# scenario analysis table
			AX4.table(
				cellText=empty,
				colLabels=['Probability of %s mm of rainfall' %self.scenario[num]], 
				bbox=[0.2, 0.9-k, 0.7, 0.12 ], 
				colColours=hdr		
			)
			#scenarios
			_aa, _ab = ascn
			_ca, _cb = cscn
			label = 'Above value', 'Below value'
			data = [_aa, _ca], [_ab, _cb]
			AX4.table(
				rowLabels=label, 
				colLabels=col, 
				cellText=data, cellLoc='center', 
				bbox=[0.2, 0.82-k, 0.7, 0.15], 
				rowColours=hdr*2
			)

		else:
			# Analog years table
			label = 'Top 1', 'Top 2', 'Top 3'
			title = ['Closest Analog Years']
			data = [angs[1]], [angs[2]], [angs[3]]
			box = [0.1, 0.82-k, 0.8, 0.18]
			AX4.table(
				rowLabels=label, 
				colLabels=title, 
				cellText=data, 
				cellLoc='center', 
				bbox=box, 
				colColours=hdr, 
				rowColours=hdr*3
			)

		# Climatology table
		label = 'Average', 'Deviation', 'Median'
		data = [aavg, avg], [astd, std], [amed, med]
		AX4.table(
			rowLabels=label, 
			colLabels=col, 
			cellText=data, 
			cellLoc='center', 
			bbox=[0.2, 0.60-k, 0.7, 0.15], 
			rowColours=hdr*3
		)

		# Assessments table
		label = 'Total', 'LTM Value', 'LTM Pct.'
		data = [atotal, etotal], [aslta, cslta], [altapct, cltapct]
		AX4.table(
			rowLabels=label, 
			colLabels=col, 
			cellText=data, 
			cellLoc='center', 
			bbox=[0.2, 0.38-k, 0.7, 0.15], 
			rowColours=hdr*3
		)

		# Projection table
		label = (
			'Average', 
			'Deviation', 
			'Median', 
			'33rd. Pctl.', 
			'67th. Pctl.', 
			'LTM Value', 
			'End of LTM'
		)
		data = (
			[eavg, cavg], 
			[estd, cstd], 
			[emed, cmed], 
			[ethrd, cthrd], 
			[esxth, csxth], 
			[aavg, avg], 
			[aepct, cepct]
		)
		AX4.table(
			rowLabels=label, 
			colLabels=col, 
			cellText=data, 
			cellLoc='center', 
			bbox=[0.2, 0.01-k, 0.7, 0.3], 
			rowColours=hdr*7
		)

		# Outlook table
		label = 'Above normal', 'Normal', 'Below normal'
		data = [AA, CA], [AN, CN], [AB, CB]
		AX4.table(
			rowLabels=label, 
			colLabels=col, 
			cellText=data, cellLoc='center', 
			bbox=[0.2, -0.21-k, 0.7, 0.15], 
			rowColours=hdr*3
		)

		# Display and savefile conditions
		fig.align_labels()
		if self.savefile:
			fig.savefig('{}/{}_rep'.format(dirpath, iD), format='png')
#=====================================================================
	def reports(self, _iD, _lta, _actyr, _acms, _asts, _cacms, _ensb, 
	            _ests, _angs, _aok, _eok, _aasts, _cests, _altm,
				_eltm, _anlist, _ascn, _cscn, dirpath):

		# Setting up from-behind season window
		ssn, deks = season(self.fst_dk, self.lst_dk, deks=True)
	
		# Iterating the plotter method
		for place in range(self.places_num):
			iD = _iD[place]
			lta = _lta[place]
			yr = _actyr[place]
			acms = _acms[place]
			asts = _asts[place]
			cacms = _cacms[place]
			ensb = _ensb[place]
			ests = _ests[place]
			angs = _angs[place]
			aok = _aok[place]
			eok = _eok[place]
			aasts = _aasts[place]
			cests = _cests[place]
			altm = _altm[place]
			eltm = _eltm[place]
			anlist = _anlist[place]
			ascn = _ascn[place]
			cscn = _cscn[place]
			self.plotter(deks, place, iD, lta, yr, ssn, acms, asts, 
			cacms, ensb, ests, angs, aok, eok, aasts, cests, altm, 
			eltm, anlist, ascn, cscn, dirpath)
		if self.showfile:
			plt.show()
#=====================================================================
