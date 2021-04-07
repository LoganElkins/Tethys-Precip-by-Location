from sqlalchemy import create_engine
import pandas as pd
import os
import uuid
import pymysql

def getAllData(limit=None, distinct=False, testingHomePage=False, latitude=None, longitude=None, location_id=None):
    sqlEngine = create_engine('mysql+pymysql://tethys_user:hfpGx6,zp@66.228.52.5', pool_recycle=3600)
    dbConnection = sqlEngine.connect()
    df = pd.DataFrame()
    if testingHomePage:
        df = pd.read_sql("select * from tethys_data.nine_month_avg_location_ids where (latitude between 30.6041 and 34.8545) and (longitude <= -81.4792 and longitude >= -89.9792) and month=(select month from tethys_data.nine_month_avg_location_ids order by month limit 1);", dbConnection)
        return df
    if location_id != None:
        df = pd.read_sql("select * from tethys_data.nine_month_avg_location_ids where location_id = {locID} order by month asc;".format(locID=location_id), dbConnection)
        return df
    if latitude != None:
        df = pd.read_sql("select * from tethys_data.nine_month_avg_location_ids where latitude = {lat} and longitude = {long};".format(lat=latitude, long=longitude), dbConnection)
        return df
    if limit == None:
        if distinct:
            df = pd.read_sql("select * from tethys_data.nine_month_avg_location_ids where month = (select month from nine_month_avg_location_ids order by month limit 1);", dbConnection)
        else:
            df = pd.read_sql("SELECT * FROM tethys_data.nine_month_avg_location_ids;", dbConnection)
    else:
            df = pd.read_sql("SELECT * FROM tethys_data.nine_month_avg_location_ids limit 0, {upperLimit};".format(upperLimit = limit), dbConnection)
    dbConnection.close()

    return df

def getLatLong(location_id):
    sqlEngine = create_engine('mysql+pymysql://tethys_user:hfpGx6,zp@66.228.52.5', pool_recycle=3600)
    dbConnection = sqlEngine.connect()
    df = pd.read_sql("select * from tethys_data.nine_month_avg_location_ids where location_id = {locID};".format(locID=location_id), dbConnection)
    latitude = df['latitude'][0]
    longtiude = df['longitude'][0]
    return latitude, longtiude