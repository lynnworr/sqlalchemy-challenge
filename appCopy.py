# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Create a session
session = Session(bind=engine)


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
def home():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)
    
    # Query for the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    # Convert the query results to a dictionary
    precipitation_dict = dict(precipitation_data)

    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # query list of stations and convert to list
    results = session.query(Station.station).all()
    stations_list = list(np.ravel(results))

    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)
    
    # Query the most active station for the last 12 months of temperature observation data
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        first()[0]
    
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= one_year_ago).\
        filter(Measurement.station == most_active_station).\
        order_by(Measurement.date).all()

    # Convert list of tuples into normal list
    temperature_list = list(np.ravel(temperature_data))

    return jsonify(temperature_list)

# Define route for temp summary for start date
@app.route("/api/v1.0/<start>")
def temp_summary_start(start):
    session = Session(engine)
    start_date_string = '2016-08-23'
    temp_summary = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date_string).all()
    session.close()
    temp_summary_list = list(np.ravel(temp_summary))
    return jsonify(temp_summary_list)


# Define route for temp summary for start and end date range
@app.route("/api/v1.0/<start>/<end>")
def temp_summary_start_end(start, end):
    session = Session(engine)
    start = '2016-08-23'
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end = '2017-08-23'
    end_date = datetime.strptime(end, '%Y-%m-%d')
    temp_summary = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    temp_summary_list = list(np.ravel(temp_summary))
    return jsonify(temp_summary_list)


if __name__ == '__main__':
    app.run(debug=True)