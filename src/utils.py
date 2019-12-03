import pandas as pd
import numpy as np
from src.const import *
from numpy.lib.stride_tricks import as_strided as strided
import matplotlib.pyplot as plt
import seaborn as sns
from mysql.connector import MySQLConnection, Error

def anonymise(df, key):
    """
    :param df: dataframe that we want to anonymize the columns of
    :param key: key for anonymization dictionary
    """

    columnNames = df.columns
    for name in columnNames:
        df.rename(columns={name: name.replace(key,dictAnon[key])}, inplace=True)

def mask_knans(df, x):
    """
    we specify a maximum of consecutive NaN we allow to be interpolated

    Example usage::

         df["col"] = df["col"].interpolate(method='linear').where(mask_knans(df["col"], int(15*60/300)))

    :param df: column of pandas dataframe
    :param x: maximum tolerance of NaN values

    :returns: boolean mapping of rows where we should interpolate
    """
    a = df
    x += 1
    a = np.asarray(a)
    k = a.size
    n = np.append(np.isnan(a), [False] * (x - 1))
    m = np.empty(k, np.bool8)
    m.fill(True)

    s = n.strides[0]
    i = np.where(strided(n, (k + 1 - x, x), (s, s)).all(1))[0][:, None]
    i = i + np.arange(x)
    i = pd.unique(i[i < k])

    m[i] = False

    return m

def countNaN(array_like):
    """
    used in combination with resampling::

        df.resample("3D").apply(countNaN)


    :param array_like: usually a partial column of dataframe

    :returns: scalar value, namely the percentage of NaN values in array_like
    """
    
    cnt = np.count_nonzero(np.isnan(array_like))
    return cnt/len(array_like)


def generateHeatmap(df,size,pmin,pmax,resampleString,preName):

    """
    generate a heatplot of the missing data, using the seaborn visualization tool


    :param df: dataframe where each column is a sensor, index is a date series
    :param size: (width, height) tuple in inches of output image
    :param pmin: min percentage where colorscale should begin :math:`\\in [0,1)`
    :param pmax: max percentage where colorscale should end :math:`\\in (0,1]`
    :param resampleString: how much should be summarized in block visually, for example "3D" = 3 days: show percentage of NaN per 3 days
    :param preName: image will be saved as :code:`preName+"_"+resampleString+".png"`
    """
    
    df2 = df.resample(resampleString).apply(countNaN)
    
    #convert date to string in desired format to display in heatmap
    as_list = df2.index.tolist()
    for i in range(len(as_list)):
        as_list[i] = as_list[i].strftime("%F")

    df6 = df2
    df6.index = as_list
    a4_dims = size #size of heatmap
    fig, ax = plt.subplots(figsize=a4_dims)
    sns.heatmap(df6.transpose(), vmin=pmin, vmax=pmax, cmap="YlGnBu",square=False, ax = ax)
    #sns.heatmap(df6.transpose(), vmin=.0, vmax=1., cmap='gist_ncar',square=False, ax = ax)

    # put the labels at 45deg since they tend to be too long
    #fig.autofmt_xdate()
    
    #plt.show()
    plt.xticks(fontsize=8, rotation=90)
    fig.savefig(preName+"_"+resampleString+".png") #save heatmap


def reportMissingData(df,freq):
    """
    writes start and end date of missing data to a csv file in the "missingData" directory
    
    :param df: dataframe with multiple sensors as columns
    :param freq: frequency as integer that df uses

    """

    sensorList = df.columns
    missingDict = {}
    for sensor in sensorList:
        #print("working on ", sensor)
        missingDatesArray = df[df[sensor].isnull()][sensor].index
        currentStartDate = missingDatesArray[0]
        lenMissingDatesArray = len(missingDatesArray)
        arrayOfMissingDates = []
        for i, el in enumerate(missingDatesArray):
            if i+1 >= lenMissingDatesArray:
                arrayOfMissingDates.append([currentStartDate, el])
            else:
                nextEl = missingDatesArray[i+1]
                timeDiff = (nextEl - el)/np.timedelta64(1,'s')
                if timeDiff > freq:
                    arrayOfMissingDates.append([currentStartDate, el])
                    currentStartDate = nextEl

        missingDict[sensor] = arrayOfMissingDates
        dfMissing = pd.DataFrame(missingDict[sensor])
        if not dfMissing.empty:
            dfMissing.to_csv("missingData/"+sensor+".csv", sep=";", header=False, index=False)