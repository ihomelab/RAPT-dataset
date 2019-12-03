#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os,sys


# In[2]:


sys.path.insert(0,"./../") #so we can import our modules properly


# In[3]:


get_ipython().run_line_magic('matplotlib', 'notebook')

#auto reload changed modules
from IPython import get_ipython
ipython = get_ipython()
ipython.magic("pylab")
ipython.magic("load_ext autoreload")
ipython.magic("autoreload 2")


from IPython.core.display import display, HTML
display(HTML("<style>.container { width:90% !important; }</style>"))
import pandas as pd

from src.const import *  # defines many of the variables used below
from src.db import *
from src.utils import *
from src.preprocessing import *


from pathlib import Path
from mysql.connector import MySQLConnection, Error


# In[4]:


if PUBLIC:
    cursor = None
else:
    config = read_db_config('./../program_config.ini', section='mysql_nonshiftable')
    conn = {}
    cursor = {}

    conn = MySQLConnection(**config)
    cursor = conn.cursor()


# ## House A

# In[5]:


filteredSensorListDB = ['_additional_power', '_dishwasher_power',  '_exp_power', '_hp_power', '_imp_power', '_sauna_power', '_stove_power', '_washing_machine_power']

dfsA = []
filteredSensorListA = []
capPeriodsA = []

getRawData(dfsA, filteredSensorListA, capPeriodsA,rawDataBaseDir, startDate=startDateA, endDate=endDateA,cursor=cursor, key=keyA, cip=cipA, filteredSensorListDB=filteredSensorListDB)
filteredSensorListA_OG = filteredSensorListA.copy()


# further prepocessing (indexing, rounding, interpolating, all in one df)

# In[6]:


alreadyProcessed = []
#capPeriodsA = [getCapturePeriodForSensorName(cursor, name) for name in filteredSensorListA_OG]
roundDuplicateEliminateInterpolateResample(dfsA,filteredSensorListA, alreadyProcessed,capPeriodsA)


# In[7]:


dfA_300s = combineDfs(dfsA,filteredSensorListA,startDateA,endDateA,"300s",300,capPeriodsA)


# rename 'A_imp_power' to 'A_total_cons_power' for consistency

# In[8]:


dfA_300s.rename(columns={'A_imp_power' : 'A_total_cons_power'}, inplace=True)


# In[9]:


pathA5min = "datasets/dfA_300s.hdf"
if os.path.exists(pathA5min):
    dfA_300s = pd.read_hdf(pathA5min, 'data')
else:
    if not os.path.exists('datasets'):
        os.mkdir('datasets')
    dfA_300s.to_hdf(pathA5min, key='data')


# missing data analysis

# In[10]:


if not os.path.exists('missingData'):
    os.mkdir('missingData')
reportMissingData(dfA_300s,300)


# generate heatmap

# In[11]:


generateHeatmap(dfA_300s,(20,7),.0,1.,"3D","A300s")


# ## House B

# In[12]:


filteredSensorListDB = ['_batt_state', '_boilertemp_bottom', '_boilertemp_top', '_boiler_heater_1_on', '_boiler_heater_2_on', '_boiler_heater_3_on', '_boiler_on_thermostat', '_boiler_power', '_direct_cons_energy', '_from_batt_energy', '_from_net_energy',  '_pv_prod_energy', '_total_cons_energy', '_to_batt_energy', '_to_net_energy']

dfsB = []
filteredSensorListB = []
capPeriodsB = []

getRawData(dfsB, filteredSensorListB, capPeriodsB,rawDataBaseDir, startDate=startDateB, endDate=endDateB,cursor=cursor, key=keyB, cip=cipB, filteredSensorListDB=filteredSensorListDB)
filteredSensorListB_OG = filteredSensorListB.copy()
convToPowerB=['B_direct_cons_energy', 'B_from_batt_energy', 'B_from_net_energy', 'B_pv_prod_energy', 'B_total_cons_energy', 'B_to_batt_energy', 'B_to_net_energy']


# Convert from energy to power

# In[13]:


convertWhToW(dfsB, filteredSensorListB, convToPowerB,  capPeriodsB)


# Calculate intergral for average power consumption for boiler

# In[14]:


boilerDfIdx = filteredSensorListB.index('B_boiler_power')
dfsB[boilerDfIdx] = preprocessBoilerPower(dfsB[boilerDfIdx],'B_boiler_power')


# further prepocessing (indexing, rounding, interpolating, all in one df)

# In[15]:


alreadyProcessed = ['B_boiler_power']
#capPeriodsB = [getCapturePeriodForSensorName(cursor, name) for name in filteredSensorListB_OG]
roundDuplicateEliminateInterpolateResample(dfsB,filteredSensorListB, alreadyProcessed,capPeriodsB)


# In[16]:


dfB_300s = combineDfs(dfsB,filteredSensorListB,startDateB,endDateB,"300s",300,capPeriodsB)


# In[17]:


pathB5min = "datasets/dfB_300s.hdf"
if os.path.exists(pathB5min) :
    dfB_300s = pd.read_hdf(pathB5min, 'data')
else:
    if not os.path.exists('datasets'):
        os.mkdir('datasets')
    dfB_300s.to_hdf(pathB5min, key='data')


# missing data analysis

# In[18]:


if not os.path.exists('missingData'):
    os.mkdir('missingData')
reportMissingData(dfB_300s,300)


# generate heatmap

# In[19]:


generateHeatmap(dfB_300s,(30,7),.0,1.,"3D","B300s")


# ## House C
# 

# conversion to power:
# `['C_direct_cons_energy','C_from_batt_energy', 'C_from_net_energy','C_pv_prod_energy,'C_total_cons_energy', 'C_to_batt_energy', 'C_to_net_energy']`
# 
# merge: `C_hh_power` and `C_total_cons_energy` to `C_total_cons_power`
# 
# special preprocessing:
# - `'C_boiler_power'`
# - `'C_hp_on_utility'`

# In[20]:


if not os.path.exists(rawDataBaseDir):
    os.mkdir(rawDataBaseDir)


# `C_hp_on_utility` was provided by the utility. Do seperate preprocessing...

# In[ ]:


path1 = 'WP-RippleCtrl-houseC_Jan16_bis_Nov16.xlsx'
path2 = 'WP-RippleCtrl-houseC_Dez16_bis_Aug19.xlsx'
name = 'C_hp_on_utility'
path_2_hdf = os.path.join(os.getcwd(), rawDataBaseDir, cipC)
os.makedirs(path_2_hdf, exist_ok=True)
path_2_hdf = os.path.join(path_2_hdf, name)+".hdf"

if os.path.exists(path1) and os.path.exists(path1):
    # Read files from the utility
    df_ripc_1 = pd.read_excel(path1, usecols=['Datum', 'Uhrzeit', 'Text'], parse_dates={'timestamp': ['Datum', 'Uhrzeit']})
    df_ripc_2 = pd.read_excel(path2, usecols=['Datum', 'Uhrzeit', 'Text'], parse_dates={'timestamp': ['Datum', 'Uhrzeit']})
    df_ripc = pd.concat([df_ripc_1, df_ripc_2])
    df_ripc.set_index('timestamp', inplace=True)
    # extract 'on' commands
    on_pattern = 'EIN'
    df_ripc[name] = df_ripc['Text'].str.contains(on_pattern)
    df_ripc[name] = df_ripc['C_hp_on_utility'].apply( lambda x: 1 if x else 0)
    df_ripc = df_ripc.drop(columns=['Text'])
    df_ripc.to_hdf(path_2_hdf, key="data")


# In[ ]:


df_ripc = pd.read_hdf(path_2_hdf)


# In[ ]:


# preprocess
capPerStr = '300s'
df_ripc.index= df_ripc.index.round(capPerStr)#round timestamps to capturePeriod
df_ripc = df_ripc[~df_ripc.index.duplicated(keep='first')]#remove possible duplicates
df_ripc = df_ripc.asfreq(capPerStr)
df_ripc.fillna(method='ffill', inplace=True)


# In[ ]:


filteredSensorListDB = ['_batt_state', '_boilertemp_bottom', '_boilertemp_top', '_boiler_heater_1_on', '_boiler_heater_2_on', '_boiler_heater_3_on', '_boiler_on_relay', '_boiler_on_thermostat', '_boiler_on_utility', '_boiler_power', '_direct_cons_energy',  '_from_batt_energy', '_from_net_energy', '_hh_power', '_hp_power',  '_pv_prod_energy', '_solarlog_radiation', '_temperature_out', '_total_cons_energy', '_to_batt_energy', '_to_net_energy',  '_weather_humidity_in', '_weather_humidity_out', '_weather_pressure', '_weather_temperature_in', '_weather_temperature_out']

dfsC = []
filteredSensorListC = []
capPeriodsC = []

getRawData(dfsC, filteredSensorListC, capPeriodsC,rawDataBaseDir, startDate=startDateC, endDate=endDateC,cursor=cursor, key=keyC, cip=cipC, filteredSensorListDB=filteredSensorListDB)
filteredSensorListC_OG = filteredSensorListC.copy()
convToPowerC = ['C_direct_cons_energy','C_from_batt_energy', 'C_from_net_energy','C_pv_prod_energy','C_total_cons_energy', 'C_to_batt_energy', 'C_to_net_energy']


# Convert from energy to power

# In[ ]:


convertWhToW(dfsC, filteredSensorListC, convToPowerC,  capPeriodsC)


# Calculate integral for average power consumption for boiler

# In[ ]:


boilerDfIdx = filteredSensorListC.index('C_boiler_power')
dfsC[boilerDfIdx] = preprocessBoilerPower(dfsC[boilerDfIdx],'C_boiler_power')


# Merge total consumption:
# merging of `'C_hh_energy'` & `'C_total_cons_energy'` (renamed to `'C_hh_power'` & `'C_total_cons_power'`), additionally  `'C_hh_power'` needs resampling

# In[ ]:


mergeTotalConsumptionC(dfsC,filteredSensorListC,filteredSensorListC_OG,capPeriodsC)


# further prepocessing (indexing, rounding, interpolating, all in one df)

# In[ ]:


alreadyProcessed = ['C_total_cons_power','C_boiler_power', 'C_hp_on_utility']
#capPeriodsC = [getCapturePeriodForSensorName(cursor, name) for name in filteredSensorListC_OG]
roundDuplicateEliminateInterpolateResample(dfsC,filteredSensorListC, alreadyProcessed,capPeriodsC)


# In[ ]:


# add C_hp_on_utility to other dataframes
dfsC.append(df_ripc)
filteredSensorListC.append('C_hp_on_utility')
capPeriodsC.append(300)


# In[ ]:


dfC_300s = combineDfs(dfsC,filteredSensorListC,startDateC,endDateC,"300s",300,capPeriodsC)
dfC_3600s = combineDfs(dfsC,filteredSensorListC,startDateC,endDateC,"3600s",3600,capPeriodsC)


# In[ ]:


pathC5min = "datasets/dfC_300s.hdf"
pathC1h = "datasets/dfC_3600s.hdf"
if os.path.exists(pathC5min) and os.path.exists(pathC1h):
    dfC_300s = pd.read_hdf(pathC5min, 'data')
    dfC_3600s = pd.read_hdf(pathC1h, 'data')
else:
    if not os.path.exists('datasets'):
        os.mkdir('datasets')
    dfC_300s.to_hdf(pathC5min, key='data')
    dfC_3600s.to_hdf(pathC1h, key='data')


# missing data analysis

# In[ ]:


if not os.path.exists('missingData'):
    os.mkdir('missingData')
reportMissingData(dfC_300s,300)
reportMissingData(dfC_3600s,3600)


# generate heatmap

# In[ ]:


generateHeatmap(dfC_300s,(40,7),.0,.1,"3D","C300s")
generateHeatmap(dfC_3600s,(40,7),.0,.1,"3D","C3600s")


# ## House D

# In[ ]:


filteredSensorListDB = ['_audio_wlan_og_power', '_dishwasher_power','_exp_power', '_hp_power', '_imp_power', '_rainwater_power', '_tumble_dryer_power',  '_washing_machine_power']

dfsD = []
filteredSensorListD = []
capPeriodsD = []

getRawData(dfsD, filteredSensorListD, capPeriodsD,rawDataBaseDir, startDate=startDateD, endDate=endDateD,cursor=cursor, key=keyD, cip=cipD, filteredSensorListDB=filteredSensorListDB)
filteredSensorListD_OG = filteredSensorListD.copy()


# start washing machine later

# In[ ]:


startDateWM = '2016-10-03 13:00:00'
washingMachineIdx = filteredSensorListD.index("D_washing_machine_power")
dfWM = dfsD[washingMachineIdx]
mask = (dfWM['DateTime'] >= pd.to_datetime(startDateWM))
dfsD[washingMachineIdx] = dfWM.loc[mask]


# further prepocessing (indexing, rounding, interpolating, all in one df)

# In[ ]:


alreadyProcessed = []
#capPeriodsD = [getCapturePeriodForSensorName(cursor, name) for name in filteredSensorListD_OG]
roundDuplicateEliminateInterpolateResample(dfsD,filteredSensorListD, alreadyProcessed,capPeriodsD)


# delete tumble dryer and rainwater for some intervals since there's so much missing data

# In[ ]:


#rainwater
s = '2016-06-15 16:35'
e = '2016-09-21 09:35'
rainwaterIdx = filteredSensorListD.index('D_rainwater_power')
dfRainWater = dfsD[rainwaterIdx]
dfRainWater[s:e] = np.nan


#tumbledryer
s = '2016-06-15 17:30'
e = '2016-09-21 09:20'

tumbleDryerIdx = filteredSensorListD.index('D_tumble_dryer_power')
dftumble = dfsD[tumbleDryerIdx]
dftumble[s:e] = np.nan


# In[ ]:


dfD_300s = combineDfs(dfsD,filteredSensorListD,startDateD,endDateD,"300s",300,capPeriodsD)


# rename 'D_imp_power' to 'D_total_cons_power' for consistency

# In[ ]:


dfD_300s.rename(columns={'D_imp_power' : 'D_total_cons_power'}, inplace=True)


# In[ ]:


pathD5min = "datasets/dfD_300s.hdf"
if os.path.exists(pathD5min):
    dfD_300s = pd.read_hdf(pathD5min, 'data')
else:
    if not os.path.exists('datasets'):
        os.mkdir('datasets')
    dfD_300s.to_hdf(pathD5min, key='data')


# missing data analysis

# In[ ]:


if not os.path.exists('missingData'):
    os.mkdir('missingData')
reportMissingData(dfD_300s,300)


# generate heatmap

# In[ ]:


generateHeatmap(dfD_300s,(30,7),.0,1.,"3D","D300s")


# ## House E

# In[ ]:


filteredSensorListDB = [ '_dehumidifier_power', '_dishwasher_power',  '_gasheating_pump_power',  '_hh_power',  '_prod_power',  '_solarheating_pump_power', '_tumble_dryer_power', '_washing_machine_power', '_weather_humidity_cellar', '_weather_humidity_in', '_weather_humidity_out', '_weather_pressure','_weather_temperature_cellar', '_weather_temperature_in', '_weather_temperature_out']
dfsE = []
filteredSensorListE = []
capPeriodsE = []

getRawData(dfsE, filteredSensorListE, capPeriodsE,rawDataBaseDir, startDate=startDateE, endDate=endDateE,cursor=cursor, key=keyE, cip=cipE, filteredSensorListDB=filteredSensorListDB)
filteredSensorListE_OG = filteredSensorListE.copy()


# further prepocessing (indexing, rounding, interpolating, all in one df)

# In[ ]:


alreadyProcessed = []
#capPeriodsE = [getCapturePeriodForSensorName(cursor, name) for name in filteredSensorListE_OG]
roundDuplicateEliminateInterpolateResample(dfsE,filteredSensorListE, alreadyProcessed,capPeriodsE)


# In[ ]:


dfE_300s = combineDfs(dfsE,filteredSensorListE,startDateE,endDateE,"300s",300,capPeriodsE)
dfE_3600s = combineDfs(dfsE,filteredSensorListE,startDateE,endDateE,"3600s",3600,capPeriodsE)


# rename 'E_hh_power' to 'E_total_cons_power' for consistency

# In[ ]:


dfE_300s.rename(columns={'E_hh_power' : 'E_total_cons_power'}, inplace=True)


# In[ ]:


pathE5min = "datasets/dfE_300s.hdf"
pathE1h = "datasets/dfE_3600s.hdf"
if os.path.exists(pathE5min) and os.path.exists(pathE1h):
    dfE_300s = pd.read_hdf(pathE5min, 'data')
    dfE_3600s = pd.read_hdf(pathE1h, 'data')
else:
    if not os.path.exists('datasets'):
        os.mkdir('datasets')
    dfE_300s.to_hdf(pathE5min, key='data')
    dfE_3600s.to_hdf(pathE1h, key='data')


# missing data analysis

# In[ ]:


if not os.path.exists('missingData'):
    os.mkdir('missingData')
reportMissingData(dfE_300s,300)
reportMissingData(dfE_3600s,3600)


# generate heatmap

# In[ ]:


generateHeatmap(dfE_300s,(30,7),.0,1.,"3D","E300s")
generateHeatmap(dfE_3600s,(30,7),.0,1.,"3D","E3600s")


# ## Missing data for all Houses

# In[ ]:


df_list = [dfA_300s, dfB_300s, dfC_300s, dfD_300s, dfE_300s]
df = pd.concat(df_list, join='outer', sort=True, axis=1)


# In[ ]:


import seaborn as sns
from matplotlib.ticker import MultipleLocator

factor = 23
size = (297/factor, 210/factor)
pmin,pmax,resampleString,preName = .0,1.,"MS","allSensors_cropped" 

df2 = df.resample(resampleString).apply(countNaN)
    
#convert date to string in desired format to display in heatmap
as_list = df2.index.tolist()
for i in range(len(as_list)):
    as_list[i] = as_list[i].strftime("%F")

df6 = df2
df6.index = as_list
df6 = df6.transpose()
fig, ax = plt.subplots(figsize=size)
sns.heatmap(df6, vmin=pmin, vmax=pmax, cmap="YlGnBu",square=False, yticklabels=1,  ax = ax)

plt.xticks(fontsize=9, rotation=90)
plt.yticks(fontsize=9)
plt.tight_layout()
fig.savefig(preName+"_"+resampleString+".png") #save heatmap


# In[ ]:




