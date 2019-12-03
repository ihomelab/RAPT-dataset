#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
sys.path.insert(0,"./../") #so we can import our modules properly


# In[ ]:


# iPhython
from IPython.core.display import display, HTML
display(HTML("<style>.container { width:90% !important; }</style>"))

from matplotlib import rcParams
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'notebook')

import numpy as np
import pandas as pd


# In[ ]:


get_ipython().run_line_magic('matplotlib', 'notebook')


# # House B 

# In[ ]:


path_to_house = "./datasets/dfB_300s.hdf"
df_house = pd.read_hdf(path_to_house)
print('\n\nStart time: {}'.format(df_house.index[1]))
print('End time: {}'.format(df_house.index[-1]))
print(df_house.columns)


# ## Check that boiler power does not exceed total consumed power

# In[ ]:


meters = ['B_boiler_power']

# Investigate only points in time where all values are available
cols = ['B_total_cons_power']
cols.extend(meters)
df_house_noNAN = df_house.loc[:,cols].dropna(axis=0, how='any')

# Check if total consumed power is larger than total of appliances
delta = df_house_noNAN.loc[:,meters].sum(axis=1) - df_house_noNAN.loc[:,'B_total_cons_power']
tmt = delta > 0

if np.any(tmt):
    print('Boiler Power is larger than total consumed power for some data points.')

    # investigate problematic cases
    print("Found {} out of {} ({:.2}%) values to be problematic.".format(tmt.sum(), len(tmt), tmt.sum()/len(tmt)*100))
    print("")
    print("Statistics of problematic values:")
    print(delta[tmt].describe())
    print()
    print((delta[tmt]/df_house_noNAN.loc[tmt, 'B_total_cons_power']).describe())
else: 
    print("Total of all appliances is smaller than total consumed energy for all measurement points.")


# In[ ]:


l = ['Total Appliances = Boiler', 'Total Consumed']
if np.any(tmt):
    print('Boiler Power is larger than total consumed power for some data points.')
    
    ## plot params ##
    ha = 6
    ncols = 8
    nrows = np.sum(tmt)//ncols+1
    fig, ax = plt.subplots(figsize=(17,3*nrows), ncols=ncols, nrows=nrows)
    idxs = np.nonzero(tmt)[0]
    for i, idx in enumerate(idxs):
        minidx = idx-ha
        maxidx = idx+ha
        df_house_noNAN.iloc[minidx:maxidx].loc[:,'B_boiler_power'].plot(ax=ax[i//ncols, i%ncols], label='Total Appliances')
        df_house_noNAN.iloc[minidx:maxidx].loc[:,'B_total_cons_power'].plot(ax=ax[i//ncols, i%ncols], label='Total Consumed')
    fig.legend(l, loc='upper center')
else: 
    print("Total of all appliances is smaller than total consumed energy for all measurement points.")


# ## Visualize Boiler Variables

# In[ ]:


fig, ax = plt.subplots(ncols=1, nrows=3, figsize=(17,12), sharex=True)
df_house.loc[:,['B_boilertemp_top', 'B_boilertemp_bottom']].plot(ax=ax[0])
ax[0].legend()
ax2 = ax[0].twinx()
df_house.loc[:,'B_boiler_power'].plot(ax=ax2, color='green')
ax2.legend()
df_house.loc[:,['B_boiler_heater_1_on', 'B_boiler_heater_2_on', 'B_boiler_heater_3_on']].plot(ax=ax[1])
ax[1].legend()
df_house.loc[:,['B_boiler_on_thermostat']].plot(ax=ax[2])
ax[2].legend()


# ## Check that `B_pv_prod_power` is the sum of `B_to_batt_power` + `B_direct_cons_power`+ `B_to_net_power`

# In[ ]:


# Investigate only points in time where all values are available
df_house_noNAN = df_house.loc[:,['B_pv_prod_power', 'B_to_batt_power', 'B_direct_cons_power', 'B_to_net_power']].dropna(axis=0, how='any')
delta = df_house_noNAN.loc[:,'B_pv_prod_power'] - df_house_noNAN.loc[:,['B_to_batt_power', 'B_direct_cons_power', 'B_to_net_power']].sum(axis=1)
print("Statistics of deviations:")
delta.describe()


# ## Check that `B_total_cons_power` is the sum of `B_direct_cons_power` + `B_from_batt_power` + `B_from_net_power`

# In[ ]:


# Investigate only points in time where all values are available
df_house_noNAN = df_house.loc[:,['B_total_cons_power', 'B_direct_cons_power', 'B_from_batt_power', 'B_from_net_power']].dropna(axis=0, how='any')
delta = df_house_noNAN.loc[:,'B_total_cons_power'] - df_house_noNAN.loc[:,['B_direct_cons_power', 'B_from_batt_power', 'B_from_net_power']].sum(axis=1)
print("Statistics of deviations:")
delta.describe()


# ## Visualize Batter Power Flows

# In[ ]:


fig, ax = plt.subplots(figsize=(17,4))
df_house.loc[:,['B_to_batt_power', 'B_from_batt_power']].plot(ax=ax)
ax.legend(loc='upper left')
ax2 = ax.twinx()
df_house.loc[:,'B_batt_state'].plot(ax=ax2, color='green')
ax2.legend(loc='lower left')


# # House B - Raw Data

# In[ ]:


import os
base_path = "../rawData/B/"
files = os.listdir(path=base_path)

blacklisted = ["capPeriods.hdf"]
for file in files:
    if file in blacklisted: continue
    print(file)
    print(os.path.join(base_path, file))
    df_rawData = pd.read_hdf(os.path.join(base_path, file))
    print(df_rawData.iloc[1,0]-df_rawData.iloc[0,0])
    print(df_rawData.iloc[-1,0]-df_rawData.iloc[-2,0])
    print()


# In[ ]:




