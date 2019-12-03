PUBLIC = True

if PUBLIC:
	from src.public import *
else:
	from src.secret import *


cipA = "A"

startDateA = '2017-04-01 00:00:00' 
endDateA = '2018-10-30 00:00:00'

cipB = "B"

startDateB = '2017-03-01 00:00:00' 
endDateB = '2019-07-31 00:00:00' 

cipC = "C"

startDateC = '2015-11-30 00:00:00' 
endDateC = '2019-07-31 00:00:00' 

cipD = "D"

startDateD = '2016-04-23 00:00:00' 
endDateD = '2019-07-31 00:00:00' 

cipE = "E"

startDateE = '2016-12-01 00:00:00' 
endDateE = '2019-07-31 00:00:00' 


rawDataBaseDir = "rawData"


resampleStringForHeatmap = "1D" 
"""
1 days, how data will be resampled to display in heatmap: examples are "3D"=3 days, "7D"=7 day, "1M"= 1 month 
"""



interpolationTime = 15
"""
max tolerance in minutes for when data should be interpolated, independent of capture period
""" 
