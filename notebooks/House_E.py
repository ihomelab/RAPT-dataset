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


# # House E 

# In[ ]:


path_to_house = "./datasets/dfE_300s.hdf"
df_house = pd.read_hdf(path_to_house)
print('\n\nStart time: {}'.format(df_house.index[1]))
print('End time: {}'.format(df_house.index[-1]))
print(df_house.columns)


# ## Total Imported Power and Total Submetered Power

# In[ ]:


meters = ['E_dehumidifier_power', 'E_dishwasher_power', 'E_gasheating_pump_power', 'E_solarheating_pump_power', 'E_tumble_dryer_power', 'E_washing_machine_power']

# Investigate only points in time where all values are available
cols = ['E_imp_power']
cols.extend(meters)
df_house_noNAN = df_house.loc[:,cols].dropna(axis=0, how='any')

# Check if total consumed power is larger than total of appliances
delta = df_house_noNAN.loc[:,meters].sum(axis=1) - df_house_noNAN.loc[:,'E_imp_power']
tmt = delta > 0

if np.any(tmt):
    # investigate problematic cases
    print("Found {} out of {} ({:.2}%) values to be problematic.".format(tmt.sum(), len(tmt), tmt.sum()/len(tmt)*100))
    print("")
    print("Statistics of problematic values:")
    print(delta[tmt].describe())
    print()
    print((delta[tmt]/df_house_noNAN.loc[tmt, 'E_imp_power']).describe())
else: 
    print("Total of all appliances is smaller than total consumed energy for all measurement points.")


# In[ ]:


l = ['Total Appliances', 'Total Consumed']
l.extend(meters)
if np.any(tmt):
    ## plot params ##
    ha = 6
    ncols = 8

    nrows = np.sum(tmt)//ncols+1
    nrows = 4
    fig, ax = plt.subplots(figsize=(17,3*nrows), ncols=ncols, nrows=nrows)
    idxs = np.nonzero(tmt)[0]
    for i, idx in enumerate(idxs[0:32]):
        minidx = idx-ha
        maxidx = idx+ha
        df_house_noNAN.loc[:,meters].sum(axis=1).iloc[minidx:maxidx].plot(ax=ax[i//ncols, i%ncols], label='Total Appliances')
        df_house_noNAN.iloc[minidx:maxidx].loc[:,'E_imp_power'].plot(ax=ax[i//ncols, i%ncols], label='Total Consumed')
        for meter in meters:
            df_house_noNAN.iloc[minidx:maxidx].loc[:,meter].plot(ax=ax[i//ncols, i%ncols], label=meter)
        ax[i//ncols, i%ncols]
    fig.legend(l, loc='upper center')
else: 
    print("Total of all appliances is smaller than total consumed energy for all measurement points.")


# # House E - Weather

# In[ ]:


path_to_house = "./datasets/dfE_3600s.hdf"
df_weather = pd.read_hdf(path_to_house)
print('\n\nStart time: {}'.format(df_weather.index[1]))
print('End time: {}'.format(df_weather.index[-1]))
print(df_weather.columns)


# In[ ]:




