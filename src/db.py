from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser

import pandas as pd
import numpy as np

from src.utils import *

def read_db_config(filename='program_config.ini', section='mysql_shiftable'):
    """
    :param filename: path to program_config.ini
    :param section: where to look for db info in .ini file
    :returns: kwargs for  MySQLConnection

    Example::

        config = read_db_config('program_config.ini', section='mysql_nonshiftable')
        connection = MySQLConnection(**config)

    """


    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))

    return db


def getSensorNamesForHouse(cursor, abbreviation):
    """
    :param cursor: db cursor
    :param abbreviation: abbrevation for house

    :returns: array of all sensors as string
    """
    query = """ SELECT NAME 
                FROM
                    Sensors 
                WHERE
                    NAME LIKE '{0}%'"""

    query = query.format(abbreviation)
    cursor.execute(query)
    rows = cursor.fetchall()
    return [r[0] for r in rows]





def getDFForQuery(cursor, query):
    """

    :param cursor: db connection cursor
    :param query: database query


    :returns: (not Empty: Bool, pandas dataframe of result)
    """
    cursor.execute(query)
        
    rows = cursor.fetchall()
    if len(rows) != 0:
        data = pd.DataFrame(rows)
        data.columns = cursor.column_names
        return (True,data)
    else:
        return (False, pd.DataFrame())

def getDFForQueryAnon(cursor, query, key):
    """

    :param cursor: db connection cursor
    :param query: database query
    :param key: key to anonymise data


    :returns: (not Empty: Bool, pandas dataframe of result which is anonymized in addition)
    """
    cursor.execute(query)
        
    rows = cursor.fetchall()
    if len(rows) != 0:
        data = pd.DataFrame(rows)
        data.columns = cursor.column_names
        anonymise(data, key)
        return (True, data)
    else:
        return (False, pd.DataFrame())


def queryForSensor(name, startD, endD):
    """
    often used in combination with getDFForQuery::

        success, result = getDFForQuery(queryForSensor("name", "2018-12-12 12:12:12", "2019-12-12 12:12:12"))

    :param name: name of sensor
    :param stardD: startdate as string
    :param endD: endDate as string:

    :returns: query string to select all values between startdate and enddate
    """
    return 'SELECT DateTime, Value as {0} FROM SensorValues as sv WHERE SensorName = "{0}" AND DateTime >= "{1}" AND DateTime < "{2}" ORDER BY DateTime'.format(name,startD,endD)

#return capturePeriod for a specific sensor name
def getCapturePeriodForSensorName(cursor, name):
    """
    assumes name exists in db

    :param cursor: db connection cursor
    :param name: name of sensor
    
    :returns: capture peroid of (sensor)name
    """


    query = """ SELECT CapturePeriod 
                FROM
                    SensorValues
                WHERE
                    SensorName = '{0}' LIMIT 1"""

    query = query.format(name)
    cursor.execute(query)
    rows = cursor.fetchall()
    return [r[0] for r in rows][0]
