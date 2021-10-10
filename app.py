#################################################
# Import Packages
#################################################
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


################################################
# Flask Setup
################################################
app = Flask(__name__)


################################################
# Flask Routes
################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/(start_date_parameter)<br/>"
        f"/api/v1.0/(start_date_parameter)/(end_date_parameter)"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Convert the query results to a dictionary using date as the key and prcp as the value."""
    # Calculate the date 1 year ago from the last data point in the database
    qry_last_row = 'SELECT date FROM measurement m ORDER BY m.id DESC LIMIT 1'
    last_date = engine.execute(qry_last_row).fetchall()
    last_date_point = last_date[0][0] # the last date in the data set

    last_date = dt.datetime.strptime(last_date_point,'%Y-%m-%d').date()
    delta = dt.timedelta(days=365)
    date_one_year_ago = last_date - delta # the date one year ago

    # Perform a query to retrieve the data and precipitation scores
    precipitation_results = session.query(Measurement.date, Measurement.prcp).    filter(Measurement.date >= date_one_year_ago).order_by(Measurement.date).all()

    session.close()
    
    # Convert query to a dictionary 
    prcp_dict = {}
    for date, prcp in precipitation_results:
        prcp_dict[date] = prcp
    
    """"Return the JSON representation of your dictionary."""
    # Return the dictionary in a JSON format
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # query the data
    stations = session.query(Station.station, Station.name).all()
    session.close()
    
    # convert it to a dictionary
    station_dict = {}
    for station, name in stations:
        station_dict[station] = name
    
    # Return the dictionary in a JSON format
    return jsonify(station_dict)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most active station id
    query = session.query(Measurement.station, func.count(Measurement.station)).    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).limit(1).all()

    station_id = query[0][0]

    # Find the last date mentioned for station 'USC00519281'
    qry_last_row = f"SELECT date, tobs FROM measurement m WHERE m.station == '{station_id}' ORDER BY m.id DESC LIMIT 1"
    last_date = engine.execute(qry_last_row).fetchall()
    last_date_point = last_date[0][0] # the last date in the data set
    last_date_point

    # Find the date one year ago for station 'USC00519281'
    last_date = dt.datetime.strptime(last_date_point,'%Y-%m-%d').date()
    delta = dt.timedelta(days=365)
    date_one_year_ago = last_date - delta # the date one year ago

    # Find the results from the last year of data for this station id
    tobs_results = session.query(Measurement.date, Measurement.tobs).    filter(Measurement.date >= date_one_year_ago, Measurement.station==most_active_station_id).    order_by(Measurement.date.asc()).all()

    # Close the session
    session.close 
    
    # Convert query to a dictionary 
    tobs_dict = {}
    for date, tobs in tobs_results:
        tobs_dict[date] = tobs
    
    """"Return the JSON representation of your dictionary."""
    # Return the dictionary in a JSON format
    return jsonify(tobs_dict)


@app.route(f'/api/v1.0/<start>')
def start(start):
     # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a JSON list of the minimum temperature, the average temperature, 
    and the max temperature for a given start or start-end range."""
    
    # Convert the start date to a datetime object 
    start_date = dt.datetime.strptime(start,'%Y-%m-%d').date()
    
    # Check if the date is valid
    first_date = session.query(Measurement.date).order_by(Measurement.id.asc()).limit(1).all()
    last_date = session.query(Measurement.date).order_by(Measurement.id.desc()).limit(1).all()
 
    first_date_object = dt.datetime.strptime(first_date[0][0],'%Y-%m-%d').date()
    last_date_object = dt.datetime.strptime(last_date[0][0],'%Y-%m-%d').date()
    
    if(start_date < first_date_object):
        return f"Please don't enter a date earlier than {first_date_object}."
    
    elif(start_date > last_date_object):
        return f"Please don't enter a date later than {last_date_object}."
    else: 
        highest_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
        
        lowest_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).all()

        average_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()

        # Close the session
        session.close 
    
        temperature_dict = {
            "TMIN" : lowest_temp[0][0],
            "TAVG" : round(average_temp[0][0],2),
            "TMAX" : highest_temp[0][0],
        }
        return jsonify(temperature_dict)


@app.route(f'/api/v1.0/<start>/<end>')
def period(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a JSON list of the minimum temperature, the average temperature, 
    and the max temperature for a given start or start-end range."""
    
    # Convert the start and end dates to datetime object 
    start_date = dt.datetime.strptime(start,'%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end,'%Y-%m-%d').date()
    
    # Check if the date is valid
    first_date = session.query(Measurement.date).order_by(Measurement.id.asc()).limit(1).all()
    last_date = session.query(Measurement.date).order_by(Measurement.id.desc()).limit(1).all()
 
    first_date_object = dt.datetime.strptime(first_date[0][0],'%Y-%m-%d').date()
    last_date_object = dt.datetime.strptime(last_date[0][0],'%Y-%m-%d').date()
    
    if(start_date < first_date_object or start_date > last_date_object):
        return f"Please don't enter a start date earlier than {first_date_object} or later than {last_date_object}."
    elif(end_date < first_date_object or end_date > last_date_object):
        return f"Please don't enter an end date earlier than {first_date_object} or later than {last_date_object}."
    else: 
        highest_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
        
        lowest_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

        average_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

        # Close the session
        session.close 
    
        temperature_dict = {
            "TMIN" : lowest_temp[0][0],
            "TAVG" : round(average_temp[0][0],2),
            "TMAX" : highest_temp[0][0],
        }
        return jsonify(temperature_dict)
    

if __name__ == '__main__':
    app.run(debug=False)