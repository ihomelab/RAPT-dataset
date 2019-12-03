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
get_ipython().run_line_magic('matplotlib', 'notebook')

import numpy as np
import pandas as pd


# # House A

# In[ ]:


path_to_house = "./datasets/dfA_300s.hdf"
df_house = pd.read_hdf(path_to_house)
print('\n\nStart time: {}'.format(df_house.index[1]))
print('End time: {}'.format(df_house.index[-1]))
print(df_house.columns)


# ## Total Imported Power and Total Submetered Power

# In[ ]:




meters = ['A_additional_power', 'A_dishwasher_power', 'A_hp_power', 'A_sauna_power', 'A_stove_power', 'A_washing_machine_power']
# Investigate only points in time where all values are available
cols = ['A_imp_power']
cols.extend(meters)
df_house_noNAN = df_house.loc[:,cols].dropna(axis=0, how='any')

# Check if total consumed power is larger than total of appliances
delta = df_house_noNAN.loc[:,meters].sum(axis=1) - df_house_noNAN.loc[:,'A_imp_power']
tmt = delta > 0

if np.any(tmt):
    # investigate problematic cases
    print("Found {} out of {} ({:.2}%) values to be problematic.".format(tmt.sum(), len(tmt), tmt.sum()/len(tmt)*100))
    print("")
    print("Statistics of problematic values:")
    print(delta[tmt].describe())
    print()
    print((delta[tmt]/df_house_noNAN.loc[tmt, 'A_imp_power']).describe())
else: 
    print("Total of all appliances is smaller than total consumed energy for all measurement points.")

    
# Found 219 out of 157804 (0.14%) values to be problematic. git commit: c32a2a752bfa71db5a31bad44ae5047fbb46b88b


# In[ ]:


l = ['Total Appliances', 'Total Consumed']
l.extend(meters)
if np.any(tmt):
    ## plot params ##
    ha = 6
    ncols = 8
    nrows = np.sum(tmt)//ncols+1
    fig, ax = plt.subplots(figsize=(24,3*nrows), ncols=ncols, nrows=nrows)
    idxs = np.nonzero(tmt)[0]
    for i, idx in enumerate(idxs):
        minidx = idx-ha
        maxidx = idx+ha
        df_house_noNAN.loc[:,meters].sum(axis=1).iloc[minidx:maxidx].plot(ax=ax[i//ncols, i%ncols], label='Total Appliances')
        df_house_noNAN.iloc[minidx:maxidx].loc[:,'A_imp_power'].plot(ax=ax[i//ncols, i%ncols], label='Total Consumed')
        for meter in meters:
            df_house_noNAN.iloc[minidx:maxidx].loc[:,meter].plot(ax=ax[i//ncols, i%ncols], label=meter)
        ax[i//ncols, i%ncols]
    fig.legend(l, loc='upper center')
else: 
    print("Total of all appliances is smaller than total consumed energy for all measurement points.")


# ## Heat Pump

# In[ ]:


fig, ax = plt.subplots(figsize=(24,5))
# df_house.loc['2017-04-01 00:00:00':'2017-04-02 23:59:59','A_hp_power'].plot(ax=ax)
df_house.loc[:,'A_hp_power'].plot(ax=ax)


# ## Sauna 

# In[ ]:


fig, ax = plt.subplots(figsize=(17,5))
# df_house.loc['2017-04-01 00:00:00':'2017-04-02 23:59:59','A_hp_power'].plot(ax=ax)
df_house.loc[:,'A_sauna_power'].plot(ax=ax)


# # House A - Raw Data

# In[ ]:


import os
base_path = "../rawData/A/"
files = os.listdir(path=base_path)

blacklisted = ["capPeriods.hdf"]
for file in files:
    if file in blacklisted: continue
    print(file)
    print(os.path.join(base_path, file))
    df_rawData = pd.read_hdf(os.path.join(base_path, file))
    print(df_rawDaxta.iloc[1,0]-df_rawData.iloc[0,0])
    print(df_rawData.iloc[-1,0]-df_rawData.iloc[-2,0])
    print()

