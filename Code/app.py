import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
        
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date in the data set.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # convert string to datetime object
    most_recent_date = list(np.ravel(most_recent_date))[0]
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')

    # convert year, month, day as seperate integers
    most_recent_year = int(dt.datetime.strftime(most_recent_date, '%Y'))
    most_recent_month = int(dt.datetime.strftime(most_recent_date, '%m'))
    most_recent_day = int(dt.datetime.strftime(most_recent_date, '%d'))

    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.date(most_recent_year, most_recent_month, most_recent_day) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
                     filter(Measurement.date >= one_year_ago, Measurement.date <= '2017-08-23').\
                     order_by(Measurement.date).all()

    #return the JSON dictionary
    return jsonify(precipitation_data)
    
@app.route("/api/v1.0/stations")
def stations():
    
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    station_name=[]
    
    for station, name in session.query(Station.station, Station.name):
        station_name.append([station, name])

    # return the JSON dictionary          
    return jsonify(station_name)
    
@app.route("/api/v1.0/tobs")
def tobs():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    
    # List the stations and the counts in descending order.
    active_stations = (session.query(Measurement.station, func.count(Measurement.station)).\
                        group_by(Measurement.station).\
                        order_by(func.count(Measurement.station).desc()).\
                        all())
    
    # determine the most active station
    most_active_id = active_stations[0][0]

    # station name
    station_name = (session.query(Station.name).filter_by(station = most_active_id))
    station_name = station_name[0][0]
    
    # Find the most recent date in the data set.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # convert string to datetime object
    most_recent_date = list(np.ravel(most_recent_date))[0]
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')

    # convert year, month, day as seperate integers
    most_recent_year = int(dt.datetime.strftime(most_recent_date, '%Y'))
    most_recent_month = int(dt.datetime.strftime(most_recent_date, '%m'))
    most_recent_day = int(dt.datetime.strftime(most_recent_date, '%d'))

    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.date(most_recent_year, most_recent_month, most_recent_day) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
                         filter(Measurement.station == most_active_id, Measurement.date >= one_year_ago, Measurement.date <= '2017-08-23').\
                         order_by(Measurement.date).all()
    
    
    return jsonify(station_name, tobs_data)
    

@app.route("/api/v1.0/<start>")
def trip1(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)


    trip_data = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
        
    trip = list(np.ravel(trip_data))
    
    return jsonify(trip)
    
@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):
    
     # Create our session (link) from Python to the DB
    session = Session(engine)

    
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()
        
    trip = list(np.ravel(trip_data))
    
    return jsonify(trip)
    

if __name__ == '__main__':
    app.run(debug=True)

    
    
    
    
    