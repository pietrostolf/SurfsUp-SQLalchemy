# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################


# Reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

# Define a function which calculates and returns the the date one year from the most recent date
def prev_year():
    # Create session
    session = Session(engine)

    # Define the most recent date in the Measurement dataset
    # Then use the most recent date to calculate the date one year from the last date
    most_recent = session.query(func.max(Measurement.date)).first()[0]
    initial_date = dt.datetime.strptime(most_recent, "%Y-%m-%d") - dt.timedelta(days=365)

    # Close session                   
    session.close()

    # Return the date
    return(initial_date)

#################################################
# Flask Routes
#################################################

# Homepage
@app.route("/")
def homepage():
    return """ <h1> Honolulu Climate API </h1>
    <ul>
    <li>Precipitation: <strong>/api/v1.0/precipitation</strong> </li>
    <li> Stations: <strong>/api/v1.0/stations</strong></li>
    <li>TOBS: <strong>/api/v1.0/tobs</strong></li>
    <li>Temperatures for a specific start date: <strong>/api/v1.0/&ltstart&gt</strong> (start date: yyyy-mm-dd)</li>
    <li>Temperatures for a specific start-end range: <strong>/api/v1.0/&ltstart&gt/&ltend&gt</strong> (start/end date: yyyy-mm-dd)</li>
    </ul>
    """

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session
    session = Session(engine)

    # Query precipitation data from last 12 months from the most recent date from Measurement table
    prep_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year()).all()
    
    # Close session                   
    session.close()

    # Create a dictionary from the row data and append to a list of prep_list
    prep_list = []
    for date, prep in prep_data:
        prep_dict = {}
        prep_dict["date"] = date
        prep_dict["prep"] = prep
        prep_list.append(prep_dict)

    # Return precipitation data for the previous year 
    return jsonify(prep_list)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    # Create session
    session = Session(engine)

    # Query station
    stat_data = session.query(Station.station).all()

    # Close session                   
    session.close()

    # Convert tuple into list
    stat_list = list(np.ravel(stat_data))

    # Return station data
    return jsonify(stat_list)

# TOBS route
@app.route("/api/v1.0/tobs")
def tobs():
    # Create session
    session = Session(engine)

    # Query the dates and temperature observations of the most-active station for the previous year of data.
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
                        filter(Measurement.date >= prev_year()).all()

    # Close session                   
    session.close()

    # Create a dictionary from the row data and append to a list of tobs_list
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    # Return tobs data for the previous year
    return jsonify(tobs_list)

# Start/Start-end range route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def cal_temp(start=None, end=None):
    # Create session
    session = Session(engine)
    
    # Check for end date
    if end == None: 
        # Query from start date
        start_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).all()
        # Convert tuples into list
        start_list = list(np.ravel(start_data))

        # Return a list of minimum, average and maximum temperatures for a start date
        return jsonify(start_list)
    else:
        # Query between start and end dates
        date_range_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()
        # Convert tuples into list
        date_range_list = list(np.ravel(date_range_data))

        # Return a list of minimum, average and maximum temperatures for a date range
        return jsonify(date_range_list)

    # Close session                   
    session.close()
    
# Define main branch 
if __name__ == "__main__":
    app.run(debug = True)
