import numpy 
import pandas
from scipy.stats import rankdata
#============================================================
'''
def year_format(number):
	return int(number // 100)
'''
year_format = lambda number: int(number // 100)
#============================================================
def Rankdata(**kwargs):
	pass
#============================================================
def read(csv_file):
	# Read raw dataset as Pandas dataframe
	data = pandas.read_csv(csv_file, header=None)

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
def SDE(past_table, present_table):

	x, y = numpy.array(present_table).shape
	dim1, dim2, dim3 = numpy.array(past_table).shape
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
def SSE(past_accums, present_accums):
	'''
	'''
	# Get the difference squared 
	x, y = numpy.array(present_accums).shape
	dim1, dim2, dim3 = numpy.array(past_accums).shape
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
def stats(vector):
	'''Computes required SMPG statistics: LTM, stDev, 
	33th/67th percentiles, 120-80% varation, and 
	LTM+/-StDev, in that order

	:param vector: Thentry 3D seasonal/ensemble array
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
		stats.append((ltm, std, thrd, sxth, mu, sgm, h, l))
		percs.append((sxth, thrd))
		
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
	y = len(percs[0])
	prob = lambda value: round((value / y) * 100)
	for place in range(x):
		row = numpy.array(ensemble[place]).transpose()[-1]
		HI, LO = percs[place]
		A, N, B = 0, 0, 0
		for yr in range(y):
			VALUE = row[yr]
			if VALUE > HI: 
				A += 1
			if VALUE < LO: 
				B += 1
			if HI >= VALUE >= LO:
				N += 1
		outlook.append((prob(A), prob(N), prob(B)))

	return outlook
#============================================================
def export_analogs(ID, data):
	'''A function that exports a CSV file with the first
	top 10 analog years for each location.

	:param ID: A vector with the name of each place.
	:param data: A vector with a dict per each place
	'''

	# Sorting dictionary by key ascending key order
	size = range(len(ID))
	data = [dict(sorted(data[i].items())) for i in size]

	# Delimiting columns and the amount of analogs
	data = [list(data[i].values())[:10] for i in size]
	cols = ['analog_{}'.format(i+1) for i in range(10)]

	# Building dataframe
	df = pandas.DataFrame(data=data, index=ID, columns=cols)
	#df.to_csv('{dir}/analogs.csv'.format(dir = dirName))

	print(df)
#============================================================
def export_summary(ID, data):
	cols = [

		    'Seasonal Avg', 'Seasonal StDev', 'Seasonal Median',  
			'Seasonal 33rd perct', 'Seasonal 67th perct', 
			'Total at current Dek', 'LTA Value', 'LTA Percentage', 
			'Ensemble Avg', 'Ensemble StDev', 'Ensemble Median', 
			'E_33rd. Perc.', 'E_67th. Perc', 'E_LTA Value', 
			'E_LTA Perc', 'Outlook: Above', 'Outlook: Normal', 
			'Outlook: Below'

			]
		
	pass
#============================================================
def export_stats():
	cols = [
		    'pctofavgatdek', 'pctofavgatEOS', 
	        'Above', 'Normal', 'Below'
		   ]






	pass
#============================================================
#============================================================
#============================================================
#============================================================
