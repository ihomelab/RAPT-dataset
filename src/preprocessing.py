import pandas as pd
import numpy as np

from src.utils import *
from src.const import *
from src.db import *

import os
import glob



def convertWhToW(dfs, sensorList, convToPower,  capPeriods):
    """
    converts energy to power, note that the column names are renamed from :code:`*energy` to :code:`*power`, everything inplace

    :param dfs: list of dataframes of various sensors
    :param sensorList: list of the respective sensorname from dfs, order should correspond to dfs
    :param capPeriods: list of capture periods of the sensornames from sensorList, order should be the same

    """
    WhToJoule = 3600
    for idx, col in enumerate(sensorList):
        if col in convToPower:
            df = dfs[idx]
            df[col] = df[col] *WhToJoule/capPeriods[idx]
            tochangeIdx = convToPower.index(col)
            sensorList[idx] = sensorList[idx].replace("energy","power")
            df.rename(columns={col: col.replace("energy","power")}, inplace=True)


def preprocessBoilerPower(df2, key):
    """
    calculates the average boiler power, because we have timestamps where the boiler is turned off/on often not following the capture period

    preprocessing is done as well (set index, interpolation)

    :param df2: dataframe of boiler 
    :param key: sensorname

    :returns: new dataframe, in a 5 min grid

    """

    toProcessDates = [pd.to_datetime('2017-10-15 02:15:02')]
    toProcessValues =[0]

    dataDict = {'DateTime' : [], key:[]}
    firstTime = True 
    for idx, row in df2.iterrows():
        ceiledTime = row["DateTime"].ceil("300s")


        if not (firstTime or ceiledTime == recentTime):
            #calculate integral
            accumVal = 0
            for i in range(1, len(toProcessDates)):
                timeDel = (toProcessDates[i] - toProcessDates[i-1]).seconds
                prevVal = toProcessValues[i-1] 
                accumVal += prevVal*timeDel

            endInterval = toProcessDates[-1].ceil("300s")
            timeDel = (endInterval - toProcessDates[-1]).seconds
            accumVal += toProcessValues[-1]*timeDel

            accumVal /= 300 # P = W /t divide by capture period

            #append to dict for new dataframe
            dataDict["DateTime"].append(endInterval)
            dataDict[key].append(accumVal)

            toProcessDates = [endInterval]
            toProcessValues = [toProcessValues[-1]]
            recentTime = ceiledTime 

        firstTime = False
        toProcessDates.append(row["DateTime"])
        toProcessValues.append(row[key])
        recentTime = ceiledTime
    dfBoil = pd.DataFrame(dataDict) 
    dfBoil = dfBoil.set_index("DateTime")
    dfBoil5min = dfBoil.asfreq("300s")
    dfBoil5min[key] = dfBoil5min[key].interpolate(method='linear').where(mask_knans(dfBoil5min[key], int(interpolationTime*60/300)))


    return dfBoil5min

#

#set DateTime columns as index, round dates (maybe resample first ?), remove duplicates, interpolate, resample to 300s
def roundDuplicateEliminateInterpolateResample(dfs, sensorList, ignoreList, capPeriods):
    """
    .. warning:: maybe resample first?

    a lot of preprocessing like: setting index, date rounding, duplicate elimination, interpolation, everything inplace

    :param dfs: list of dataframes, where each is a sensor
    :param sensorList: list of sensornames, same order as dfs
    :param ignoreList: do not touch the sensors mentiones in this list
    :param capPeriods: list of all capturePeriods, same order as sensorList (and length)

    """

    global interpolationTime
    for i, name in enumerate(sensorList):
        if not name in ignoreList:
            capPer = capPeriods[i]
            capPerStr = str(capPer)+"s"
            dfs[i] = dfs[i].set_index("DateTime")
            dfs[i].index= dfs[i].index.round(capPerStr)#round timestamps to capturePeriod
            dfs[i] = dfs[i][~dfs[i].index.duplicated(keep='first')]#remove possible duplicates
            dfs[i] = dfs[i].asfreq(capPerStr)
            interpLimit = int(interpolationTime*60/capPer)
            if interpLimit == 0:#for weather data (hourly)
                interpLimit = 3 #3 hours of missing data will be interpolated
            numNaVal= dfs[i][name].isna().sum()
            dfs[i][name] = dfs[i][name].interpolate(method='linear').where(mask_knans(dfs[i][name], interpLimit))
            numNaVal= numNaVal - dfs[i][name].isna().sum()
            #print(name, numNaVal)
            if capPer != 300 and capPer != 3600:
                dfs[i] = dfs[i].resample("300s", label='right', closed='right').mean()
                capPeriods[i] = 300

                
#combine all single dfs into one big df        
def combineDfs(dfs, sensorList,  startDate,endDate,freq, freqInt,capPeriods):
    """
    combine all dataframes into one big one, while merging all columns

    :param dfs: list of dataframes we want to merge
    :param sensorList: list of sensornames, same order as dfs
    :param startDate: global startDate we want to choose
    :param endDate: global endDate we want to choose
    :param freq: frequency as string that we want in the merged dataframe
    :param freqInt: frequency as integer that we want in the merged dataframe
    :param capPeriods: list of capture periods, same order and length as sensorList

    :returns: merged dataframe

    """

    t_index = pd.DatetimeIndex(start=startDate, end=endDate, freq=freq)

    df_templ = pd.DataFrame({'DateTime': t_index, 'dummy': [0 for x in range(len(t_index))]})
    df_templ = df_templ.set_index(t_index)
    for i, name in enumerate(sensorList):
        if capPeriods[i] == freqInt:
            df_templ[name]= dfs[i][name]

    df_templ = df_templ.drop(columns=['dummy', "DateTime"])
    
    return df_templ


def saveDFS(dfs, basedir,subdir):
    """
    saving raw data from MySQL database

    :param dfs: list of dataframes, each dataframe is a sensor
    :param basedir: filepath is constructed like this: :code:`os.path.join(basedir,os.path.join(subdir,sensorname))+".hdf"`
    :param subdir: see description of basedir
    """
    
    for df in dfs:
        name = df.columns[-1]
        df.to_hdf(os.path.join(basedir,os.path.join(subdir,name))+".hdf", key="data")


def readDFS(dfs, basedir,subdir, sensorList):
    """
    reads the raw data into a list of dataframes
    
    :param dfs: we store the hdf files that are read in this list
    :param basedir: we expect files to be in :code:`os.path.join(basedir,os.path.join(subdir,sensorname))+".hdf", key="data")`
    :param subdir: see description of param basedir
    :param sensorList: this list gets filled with names of the sensors in dfs, the order is the same as in dfs

    """
    mypath = os.path.join(os.path.join(basedir,subdir),"*.hdf")
    
    files = glob.glob(mypath)
    del sensorList[:]
    del dfs[:]
    for f in files:
        if "capPeriods".lower() in f.lower():
            continue
        if "c_hp_on_utility".lower() in f.lower():
            continue
        df = pd.read_hdf(f, "data")
        name = df.columns[-1]
        sensorList.append(name)
        dfs.append(df)
    return len(dfs) != 0

def saveCapPeriods(capPeriods,filteredSensorList, basedir,subdir):
    """
    aux function to save the capture periods of the sensors in a hdf file

    :param capPeriods: list of capture periods
    :param filteredSensorList: list of sensor names, same order as capPeriods
    :param basedir: file is saved in :code:`os.path.join(basedir,os.path.join(subdir,"capPeriods"))+".hdf", key="data")`
    :param subdir: see description of basedir
    """
    dataDict = {}
    capPeriodsCus = [[x] for x in capPeriods]
    for i in range(len(filteredSensorList)):
        dataDict[filteredSensorList[i]] = capPeriodsCus[i]
    metaDF = pd.DataFrame.from_dict(dataDict)
    name = "capPeriods"
    metaDF.to_hdf(os.path.join(basedir,os.path.join(subdir,name))+".hdf",key="data")

def readCapPeriods(capPeriods,filteredSensorList, basedir,subdir):
    """
    aux function to read  the capture periods of the sensors from a hdf file
    
    :param capPeriods: capture periods get stored in here
    :param filteredSensorList: list of sensor names, same order as capPeriods will be
    :param basedir: file is expected in :code:`os.path.join(basedir,os.path.join(subdir,"capPeriods"))+".hdf", key="data")`
    :param subdir: see description of basedir
    """
    name = "capPeriods"
    metaDF = pd.read_hdf(os.path.join(basedir,os.path.join(subdir,name))+".hdf","data")
    dataDict={}
    for el in metaDF.columns:
        dataDict[el]= metaDF[el][0]

    del capPeriods[:]

    for el in filteredSensorList:
        capPeriods.append(dataDict[el])


def getRawData(dfs, filteredSensorListRet, capPeriods, basedir,cip,startDate=None,endDate=None, cursor=None, key=None,  filteredSensorListDB=None):
    """
    We check first if there are raw datafiles available in :code:`basedir/cip`. If there aren't any, we load the data from the MySQL db, but only if there is a cursor given. After loading the data from the database we store it in basedir/subdir
    
    .. warning:: if there is no raw data hdf files present in :code:`basedir/cip` and no cursor is provided, the function simply returns and nothing happens


    :param dfs: we load the dataframes of each sensor into this list
    :param filteredSensorListRet: in this list we put the sensornames, the order is the same as in dfs
    :param capPeriods: in this list we put the capture periods of tje sensors, the order is the same as in dfs
    :param basedir: the rawdata is expected/stored in :code:`basedir/cip`
    :param cip: anonymized name of house
    :param startDate: only required when we load the data from the db, not required if there are hdf files present
    :param endDate: only required when we load the data form the db, not required if there are hdf files present
    :param cursor: the db connection cursor, not required if there are hdf files present
    :param key: shortName of house, not required if there are hdf files present
    :param filteredSensorListDB: sensors we want to load from db; the actual names are constructed like this: :code:`[key+'{0}'.format(i) for i in filteredSensorListDB]`, not required if there are hdf files present

    """
    
    if readDFS(dfs, basedir, cip, filteredSensorListRet):

        readCapPeriods(capPeriods,filteredSensorListRet, rawDataBaseDir, cip)
        print("found raw hdf files")
    else:
        print("access database to get data")
        if cursor is None:
            print("need to access db, no db cursor given, abort")
            return
        filteredSensorList = [key+'{0}'.format(i) for i in filteredSensorListDB]
        filteredSensorListAnon = [cip+'{0}'.format(i) for i in filteredSensorListDB]

        capPeriods.extend([getCapturePeriodForSensorName(cursor, name) for name in filteredSensorList])

        del dfs[:]

        for l in filteredSensorList:
            succ, res = getDFForQueryAnon(cursor,queryForSensor(l, startDate,endDate), key)
            if succ:
                dfs.append(res)
            else: 
                dfs.append(pd.DataFrame())

        if not os.path.exists(os.path.join(rawDataBaseDir, cip)):
            os.makedirs(os.path.join(rawDataBaseDir, cip))
        saveDFS(dfs, rawDataBaseDir,cip)
        saveCapPeriods(capPeriods,filteredSensorListAnon, rawDataBaseDir,cip)
        filteredSensorListRet.extend(filteredSensorListAnon)

def mergeTotalConsumptionC(dfs, filteredSensorList,filteredSensorList_OG,capPeriods):
    """
    special preprocessing function for house C to merge the two sensors that measure the total consumption

    :param dfs: list of dataframes, each dataframe contains values of one sensor
    :param filteredSensorList: name of the sensors, order is the same as in dfs
    :param filteredSensorList_OG: unmodified version, of filteredSensorList
    :param capPeriods: capture periods of all sensors, order is the same as dfs

    """
    HHPowerDfIdx = filteredSensorList.index('C_hh_power')
    TotalConsPowerDfIdx = filteredSensorList.index('C_total_cons_power')
    dfHHPower=dfs[HHPowerDfIdx]
    dfTotalCons=dfs[TotalConsPowerDfIdx]

    dfHHPower=dfHHPower.set_index("DateTime")
    dfTotalCons = dfTotalCons.set_index("DateTime")


    interpLimitHHPower = int(interpolationTime*60/120)
    interpLimitTotalCons = int(interpolationTime*60/300)

    #insert NaN for missing values
    dfHHPower.index= dfHHPower.index.round("120s")
    dfTotalCons.index= dfTotalCons.index.round("300s")
    dfHHPower = dfHHPower[~dfHHPower.index.duplicated(keep='first')]
    dfTotalCons = dfTotalCons[~dfTotalCons.index.duplicated(keep='first')]

    dfHHPower = dfHHPower.asfreq("120s")
    dfTotalCons = dfTotalCons.asfreq("300s")

    dfHHPower['C_hh_power']= dfHHPower['C_hh_power'].interpolate(method='linear').where(mask_knans(dfHHPower['C_hh_power'], interpLimitHHPower))
    dfTotalCons['C_total_cons_power'] = dfTotalCons['C_total_cons_power'].interpolate(method='linear').where(mask_knans(dfTotalCons['C_total_cons_power'], interpLimitTotalCons))

    dfHHPower= dfHHPower.resample("300s").mean()
    dfHHPower.rename(columns={'C_hh_power':'C_total_cons_power'},inplace=True)
    dfTotalConsPowerComb = dfHHPower.append(dfTotalCons)

    #put back in dfs array

    del filteredSensorList[HHPowerDfIdx]
    del filteredSensorList_OG[HHPowerDfIdx]
    del capPeriods[HHPowerDfIdx]
    del dfs[HHPowerDfIdx]
    

    TotalConsPowerDfIdx = filteredSensorList.index('C_total_cons_power')
    dfs[TotalConsPowerDfIdx] = dfTotalConsPowerComb

