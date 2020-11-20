# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 Jeaustin Sirias
#
import os
import numpy 
import pandas
from scipy.stats import rankdata
#============================================================
year_format = lambda number: int(number // 100)
#============================================================
prob = lambda value, y: round((value / y) * 100)
#============================================================
def season(fst_dek, lst_dek, deks=False):
	'''Computes the seasonal window params to 
	simplify coding in the core module.

	:param fst_dek: first dekad in the season
	:param lst_dek: last dekad in the season
	:param getdeks: If false, only returns season len
	:return: season length, season dekads
	'''
	lib = spawn_deks()
	dekads = dek_list()
	start = lib[fst_dek]
	end = lib[lst_dek] 

	# Conditioning
	if start < end:
		season = len(range(start, end+1))
		dekads = dekads[start:end+1]
	else:
		a = len(range(start, 36))
		b = len(range(0, end+1))	
		season = a + b
		dekads = dekads[start:] + dekads[:end+1]
	
	if deks == False:
		return season, start
	else:
		return season, dekads
#============================================================
def read(csv_file):
	'''Imports the raw rainfall dataset and shreds it
	into ID location codes and raw data.

	:param csv_file: CSV dataset
	:return: init and end year, raw data and IDs
	'''
	# Read raw dataset as Pandas dataframe
	data = pandas.read_csv(
		csv_file, 
		header=None, 
		dtype={0:object},
		keep_default_na=False
	)

	# Choose first year
	fst_yr = year_format(int(data.loc[0][1]))

	# Filter locations ID/names
	ID = list(data[0].loc[1:])
	
	# if there are scenarios:
	if data.loc[0].iloc[-1] == 'scenario':
		lst_yr = year_format(data.loc[0].iloc[-2])

		# scenarios
		scenarios = data.iloc[1:,-1:].replace([''], [-1])
		scenarios = numpy.array(scenarios, dtype=int)
		scenarios = scenarios.transpose()[0]

		# Dataset
		raw_data = []
		for i in range(len(ID)):
			location = list(data.loc[i+1][1:-1])
			raw_data.append(location)
		raw_data = numpy.array(raw_data, dtype=float)

		return fst_yr, lst_yr, ID, raw_data, scenarios
	#if not:
	else:
		lst_yr = year_format(int(data.loc[0].iloc[-1]))
		raw_data = []
		for i in range(len(ID)):
			location = list(data.loc[i+1][1:])
			raw_data.append(location)
		raw_data = numpy.array(raw_data, dtype=float)

		return fst_yr, lst_yr, ID, raw_data, []
#============================================================
def spawn_deks():
	'''
	:return: a standard dictionary of dekads
	'''
	DEK = {
		   '1-Jan':  0, '2-Jan':  1, '3-Jan': 2, '1-Feb':  3, 
		   '2-Feb':  4, '3-Feb':  5, '1-Mar': 6, '2-Mar':  7, 
		   '3-Mar':  0, '1-Apr':  9, '2-Apr':10, '3-Apr': 11, 
		   '1-May': 12, '2-May': 13,'3-May': 14, '1-Jun': 15, 
		   '2-Jun': 16, '3-Jun': 17,'1-Jul': 18, '2-Jul': 19, 
		   '3-Jul': 20, '1-Aug': 21,'2-Aug': 22, '3-Aug': 23, 
		   '1-Sep': 24, '2-Sep': 25,'3-Sep': 26, '1-Oct': 27, 
		   '2-Oct': 28, '3-Oct': 29,'1-Nov': 30, '2-Nov': 31, 
		   '3-Nov': 32, '1-Dec': 33,'2-Dec': 34, '3-Dec': 35
	}

	return DEK
#============================================================
def sdE(past_table, present_table):
	''' Computes the sum of dekad error.
	
	:param past_table: 
	:param present_table:
	:return: A sum dekad error vector
	'''

	x, y = numpy.array(present_table).shape
	dim2= numpy.array(past_table).shape[1]
	SDE = []
	# Compute diff by dekad, squared. 
	for place in range(x):
		a = present_table[place] # present year
		yr = []
		for year in range(dim2):
			b = past_table[place][year] # past years
			sde = [pow(a[i]-b[i], 2) for i in range(y)]
			sde = sum(sde)
			yr.append(sde)

		SDE.append(rankdata(yr, method='ordinal'))

	return SDE
#============================================================
def ssE(past_accums, present_accums):
	'''
	'''
	# Get the difference squared 
	x, y = numpy.array(present_accums).shape
	dim2 = numpy.array(past_accums).shape[1]
	SSE = []
	rank = []

	for place in range(x):
		row = []
		VAL = present_accums[place][-1]
		for year in range(dim2):
			DIFF = past_accums[place][year][y-1] - VAL
			sse = pow(DIFF, 2)
			row.append(sse)
		SSE.append(row)

	# Rank data
	for place in range(x):
		rnk = rankdata(SSE[place], method='ordinal')
		rank.append(rnk)

	return rank
#============================================================
def dek_list():
	DEK = [
		   '1-Jan', '2-Jan', '3-Jan', '1-Feb', '2-Feb', 
		   '3-Feb', '1-Mar', '2-Mar', '3-Mar', '1-Apr', 
		   '2-Apr', '3-Apr', '1-May', '2-May', '3-May', 
		   '1-Jun', '2-Jun', '3-Jun', '1-Jul', '2-Jul', 
		   '3-Jul', '1-Aug', '2-Aug', '3-Aug', '1-Sep', 
		   '2-Sep', '3-Sep', '1-Oct', '2-Oct', '3-Oct', 
		   '1-Nov', '2-Nov', '3-Nov', '1-Dec', '2-Dec', 
		   '3-Dec'
	]

	return DEK
#============================================================
def Stats(vector, extrapercs=False):
	'''Computes required SMPG statistics: LTM, stDev, 
	33th/67th percentiles, 120-80% varation, and 
	LTM+/-StDev, in that order

	:param vector: Thentry 3D seasonal/ensemble array
	:param extrapercs: If false just retuns stats
	:return: 2D statistics vector
	'''
	stats = []
	percs = []
	x, y, z = numpy.array(vector).shape

	for place in range(x):
		location = numpy.array(vector[place]).transpose()
		ltm = [numpy.mean(location[i]) for i in range(z)]
		lst_row = location[-1]
		avg = ltm[-1]

		# Computing stats per location
		std = round(numpy.std(lst_row))
		thrd = round(numpy.percentile(lst_row, 33))
		sxth = round(numpy.percentile(lst_row, 67))
		mu = round(avg + std)
		sgm = round(avg - std)
		h = [i * 1.2 for i in ltm]
		l = [i * 0.8 for i in ltm]
		Avg = round(numpy.mean(lst_row))
		Med = round(numpy.median(lst_row))
		stats.append([ltm, std, thrd, sxth, mu, sgm, h, l, Avg, Med])
		percs.append((sxth, thrd))

	if extrapercs == False:	
		return stats
	else:
		return stats, percs
#============================================================
def outlook(percs, ensemble):
	'''Computes the probability at the en of the season
	by clasifiyng how many past years are above 67th perc,
	between 67th and 33rd percs and below 33rd perc from
	seasonal climatological stats.

	:param percs: array of 33rd and 67th percs tuples
	:param ensemble: climatological or analog ensemble arr
	:return outlook:
	'''
	outlook = []
	#x, y, z = numpy.array(ensemble).shape
	x = len(percs)
	y = len(ensemble[0])
	for place in range(x):
		row = numpy.array(ensemble[place]).transpose()[-1]
		HI, LO = percs[place]
		A, N, B = 0, 0, 0
		for yr in row:
			if yr > HI: 
				A += 1
			elif yr < LO: 
				B += 1
			elif HI >= yr >= LO:
				N += 1
		outlook.append((prob(A, y), prob(N, y), prob(B, y)))

	return outlook
#============================================================
def export_analogs(ID, data, dirpath):
	'''A function that exports a CSV file with the first
	top 10 analog years for each location.

	:param ID: A vector with the name of each place.
	:param data: A vector with a dict per each place
	:return: nothing
	'''
	if dirpath == None:
		return

	# Sorting dictionary by ascending key order
	size = range(len(ID))
	data = [dict(sorted(data[i].items())) for i in size]

	# Delimiting columns and the amount of analogs
	data = [list(data[i].values())[:10] for i in size]
	cols = ['analog_{}'.format(i+1) for i in range(10)]

	# Building dataframe
	df = pandas.DataFrame(data=data, index=ID, columns=cols)
	df.to_csv('{dir}/analogs.csv'.format(dir = dirpath))
#============================================================
def export_summary(iD, ca_stats, ce_stats, ltm_stats, dirpath):
	'''Exports all climatological statistics from the spawned
	tables in the reports.

	:param iD: Locations' names vector
	:param:
	:param:
	:param:
	:param:
	:return: nothing
	'''
	if dirpath == None:
		return
	cols = [
		'Seasonal_StDev', 
		'Seasonal_33rd_pctl', 
		'Seasonal_67th_pctl', 
		'Avg+StDev', 
		'Avg-StDev', 
		'Seasonal_Avg', 
		'Seasonal_Med', 
		'Total_current_Dek', 
		'LTA_val', 
		'LTA_pct', 
		'Ensemble_StDev', 
		'E_33rd_pct.', 
		'E_67th_pct', 
		'E_Avg+StDev', 
		'E_Avg-StDev', 
		'Ensemble_Avg', 
		'Ensemble_Med',
		'E_LTA_Value', 
		'E_LTA_pct'
	]
	sts1 = []
	sts2 = []
	nums = [1, 2, 3, 4, 5, 8, 9]
	for place in range(len(iD)):
		ses = []
		ens = []
		for i in nums:
			s = ca_stats[place][i]
			e = ce_stats[place][i]
			ses.append(s)
			ens.append(e)
		sts1.append(ses)
		sts2.append(ens)

	# Transposing to set variables as columns
	sts1 = numpy.array(sts1).transpose()
	sts2 = numpy.array(sts2).transpose()
	ltm_stats = numpy.array(ltm_stats).transpose()
	
	dsv, pct3, pct6, mu, sgm, avg, m = sts1
	edsv, epct3, epct6, emu, esgm, eavg, em = sts2
	a, b, c, d = ltm_stats

	data = numpy.array([dsv, pct3, pct6, mu, sgm, avg, m, 
	     a, b, c, edsv, epct3, epct6, emu, esgm, eavg, em, 
		 avg, d]).transpose()

	#print(data)
	df = pandas.DataFrame(data=data, index=iD, columns=cols)
	df.to_csv('{dir}/statistics.csv'.format(dir = dirpath))	
#============================================================
def export_stats(iD, ltm_stats, outlook, dirpath):
	'''Computes a summary of probabilities based on LTA
	percentages and the probability at the end of season.

	:param ltm_stats: climatological long term stats 
	:param outlook: Probability of rainfall at the end.
	:param dirpath: file directory to save CSV file
	:return: nothing
	'''
	if dirpath == None:
		return
	
	PCT, EPCT = numpy.array(ltm_stats).transpose()[2:]
	AN, NN, BN = numpy.array(outlook).transpose()
	data = numpy.array([PCT, EPCT, AN, NN, BN]).transpose()
	cols = [
		    'pctofavgatdek', 
			'pctofavgatEOS', 
	        'Above', 
			'Normal', 
			'Below'
	]
	df = pandas.DataFrame(data=data, index=iD, columns=cols)
	df.to_csv('{dir}/summary.csv'.format(dir = dirpath))	
#============================================================
def lt_stats(act_accums, sstats, estats):
	'''Computes the long term average statistics for
	seasonal and ensemble featured tables. This function
	must be optimized next versions.

	:param act_accums: current year accumulations vector
	:param sstats: seasonal statistics vector
	:param estats: ensemble statistics vector
	:return: LTA statistics vector
	'''
	lt_sts = []
	LOCS, SIZE = numpy.array(act_accums).shape
	for place in range(LOCS):
		TOTAL = round(act_accums[place][-1])
		LTA = round(sstats[place][0][SIZE-1])
		PCT = round((TOTAL / LTA) * 100)
		AVG = sstats[place][8]
		EAVG = estats[place][8]
		EPCT = round((EAVG / AVG) * 100)
		lt_sts.append([TOTAL, LTA, PCT, EPCT])

	return lt_sts
#============================================================
def filepath(rel_path, *filenames):
	'''A method to get the absolute path for a file 
	directory. It solves the relative path problem when
	a .py asks for a file that is not in its directory.

	:param rel_path: the relative path i.e, '/images/'
	:param *filenames: A tuple with the files names
	:return: a string with the absolute path of a file
	'''
	path = os.path.dirname(__file__)
	abspath = os.path.join(path, rel_path)
	paths = [abspath + files for files in filenames]
	return paths
#============================================================
#============================================================



'''
fst_yr, lst_yr, ID, raw_data, scenarios = read('sample2.csv')
raw_data = numpy.array(raw_data)
raw_data=raw_data.astype(float)
print(int('scenario'))
'''

'''
data = pandas.read_csv('sample2.csv', header=None, dtype={0:object}, keep_default_na=False)
scenarios = data.iloc[1:,-1:].replace([''], [-1])
#scenarios = numpy.array(scenarios, dtype=int).transpose()[0]

#scn = data['scenario'].head()
print(scenarios)
'''
