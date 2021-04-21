from sqlalchemy import create_engine, Column, Integer, Float, String, Date, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from scipy.spatial import KDTree
from .app import PrecipByLocation as app
import pandas as pd
import os
import uuid
import pymysql

Base = declarative_base()

def getAllData(limit=None, distinct=False, testingHomePage=False, latitude=None, longitude=None, location_id=None):
    username = ""
    password = ",zp"
    sqlEngine = create_engine('mysql+pymysql://{user}:{passwd}@66.228.52.5'.format(user=username, passwd=password), pool_recycle=3600)
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

def getAllDataNew(location_id_param):
    Session = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()
    locations = session.query(Location).filter(Location.location_id == location_id_param)
    return pd.read_sql(locations.statement, locations.session.bind)  

def getLatLong(location_id):
    username = ""
    password = ""
    sqlEngine = create_engine('mysql+pymysql://{user}:{passwd}@66.228.52.5'.format(user=username, passwd=password), pool_recycle=3600)
    dbConnection = sqlEngine.connect()
    df = pd.read_sql("select * from tethys_data.nine_month_avg_location_ids where location_id = {locID};".format(locID=location_id), dbConnection)
    latitude = df['latitude'][0]
    longtiude = df['longitude'][0]
    return latitude, longtiude

def getLocID(lat, userLong):
    username = ""
    password = ""
    Session = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()
    locations = session.query(Location).filter(and_(Location.latitude == lat, Location.longitude == userLong))
    df = pd.read_sql(locations.statement, locations.session.bind)
    return df['location_id'][0].item()

def getClosestLatLong(latitude, longitude):
    username = ""
    password = ""
    # sqlEngine = create_engine('mysql+pymysql://{user}:{passwd}@66.228.52.5'.format(user=username, passwd=password), pool_recycle=3600)
    # dbConnection = sqlEngine.connect()
    # df = pd.read_sql("SELECT distinct latitude, longitude FROM tethys_data.nine_month_avg_location_ids order by latitude asc, longitude asc", dbConnection)
    Session = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()
    locations = session.query(Location.latitude, Location.longitude).group_by(Location.latitude, Location.longitude)
    session.close()
    df = pd.read_sql(locations.statement, locations.session.bind)    
    df_array = df.to_numpy()
    kdtree = KDTree(df_array)
    d, i = kdtree.query((latitude, longitude))
    return df_array[i][0], df_array[i][1]

def getAllLocations():
    Session = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()
    locations = session.query(Location).filter(and_(Location.latitude >= 30.6041, Location.latitude <= 34.8545, Location.longitude >= -89.9792, Location.longitude <= -81.4792))
    session.close()

    return locations

class Location(Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    prcp = Column(Float)
    tave = Column(Float)
    tmax = Column(Float)
    tmin = Column(Float)
    county_state = Column(String)
    month = Column(Date)

def initPrimaryDB(engine, first_time):
    from datetime import datetime
    Base.metadata.create_all(engine)

    if first_time:
        Session = sessionmaker(bind=engine)
        session = Session()
        df = getAllData()
        initialMon = df['month'][0]
        for index, row in df.iterrows():
            if(row['month'] != initialMon):
                print("Finished " + initialMon)
                session.commit()
                initialMon = row['month']
            location = Location(
                location_id = row['location_id'],
                latitude = row['latitude'],
                longitude = row['longitude'],
                prcp = row['prcp'],
                tave = row['tave'],
                tmin = row['tmin'],
                tmax = row['tmax'],
                county_state = row['county_state'],
                month =  datetime.strptime(row['month'], "%Y-%m-%d")
            )
            session.add(location)
        session.commit()
        session.close()