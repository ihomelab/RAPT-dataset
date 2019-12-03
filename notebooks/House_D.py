#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys, os
sys.path.insert(0,"./../") #so we can import our modules properly


# In[ ]:


# iPhython
from IPython.core.display import display, HTML
display(HTML("<style>.container { width:90% !important; }</style>"))

from matplotlib import rcParams
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'notebook')
get_ipython().run_line_magic('matplotlib', 'notebook')

import numpy as np
import pandas as pd


# # House D

# In[ ]:


path_to_house = "./datasets/dfD_300s.hdf"
df_house = pd.read_hdf(path_to_house)
print('\n\nStart time: {}'.format(df_house.index[1]))
print('End time: {}'.format(df_house.index[-1]))
print(df_house.columns)


# ## Total Imported Power and Total Submetered Power

# In[ ]:


meters = ['D_audio_wlan_og_power', 'D_dishwasher_power', 'D_hp_power', 'D_rainwater_power', 'D_tumble_dryer_power', 'D_washing_machine_power']

# Investigate only points in time where all values are available
cols = ['D_imp_power']
cols.extend(meters)
df_house_noNAN = df_house.loc[:,cols].dropna(axis=0, how='any')


total_consumers_house = df_house_noNAN.loc[:,meters].sum(axis=1)
# Check if total consumed power is larger than total of appliances
delta = total_consumers_house - df_house_noNAN.loc[:,'D_imp_power']
tmt = delta > 0

if np.any(tmt):
    # investigate problematic cases
    print("Found {} out of {} ({:.2}%) values to be problematic.".format(tmt.sum(), len(tmt), tmt.sum()/len(tmt)*100))
    print("")
    print("Statistics of problematic values:")
    print(delta[tmt].describe())
    print()
    print((delta[tmt]/df_house_noNAN.loc[tmt, 'D_imp_power']).describe())
else: 
    print("Total of all appliances is smaller than total consumed energy for all measurement points.")


# In[ ]:


l = ['Total Appliances', 'Total Consumed']
l.extend(meters)
if np.any(tmt):
    ## plot params ##
    ha = 6
    ncols = 2
    nrows = np.sum(tmt)//ncols+1
    nrows = 2
    fig, ax = plt.subplots(figsize=(24,3*nrows), ncols=ncols, nrows=nrows)
    idxs = np.nonzero(tmt)[0]
    for i, idx in enumerate(idxs[0:2]):
        minidx = idx-ha
        maxidx = idx+ha
        total_consumers_house.iloc[minidx:maxidx].plot(ax=ax[i//ncols, i%ncols], label='Total Appliances')
        df_house_noNAN.iloc[minidx:maxidx].loc[:,'D_imp_power'].plot(ax=ax[i//ncols, i%ncols], label='Total Consumed')
        for meter in meters:
            df_house_noNAN.iloc[minidx:maxidx].loc[:,meter].plot(ax=ax[i//ncols, i%ncols], label=meter)
        ax[i//ncols, i%ncols]
    fig.legend(l, loc='upper center')
else: 
    print("Total of all appliances is smaller than total consumed energy for all measurement points.")


# # House D - Raw Data

# In[ ]:


# import necessary constants and functions
from src.const import cipD, startDateD, endDateD, rawDataBaseDir
from src.preprocessing import getRawData

