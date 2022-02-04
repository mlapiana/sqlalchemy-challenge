import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
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
        f"/api/v1.0/start/yyyy-mm-dd<br/>"
        f"/api/v1.0/start/end/yyyy-mm-dd/yyyy-mm-dd"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query precipitation
    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

    # Convert list of tuples into normal list
    precipitation = []
    for date,prcp in results:
        
        # Eliminate missing data
        if prcp is not None:
            precipitation_dict = {}
            precipitation_dict[date] = prcp
            precipitation.append(precipitation_dict)
        
    print(f'Total result {len(precipitation)} rows')
    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Station.station,Station.name,Station.latitude, Station.longitude,Station.elevation).all()

    session.close()

    # Convert list of tuples into normal list
    station = [{'ID':result[0],'Name':result[1],'LAT':result[2],'LONG':result[3],'ELEV':result[4]} for result in results ]

    return jsonify(station)


@app.route("/api/v1.0/tobs")
def TOBs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Dates for past 12 months
    date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent_date = dt.date(int(date.split('-')[0]),int(date.split('-')[1]),int(date.split('-')[2]))
    query_date = most_recent_date - dt.timedelta(days=365)

    # Most active station
    count = func.count(Measurement.date)
    most_active_station = session.query(Measurement.station,count).group_by(Measurement.station).order_by(count.desc()).first()

    # Query 1-year tobs for the most activate station
    results = session.query(Measurement.date,Measurement.tobs).filter(Measurement.station==most_active_station[0]).filter(Measurement.date >= query_date).all()

    session.close()

    # Convert list of tuples into normal list
    one_year_temp = []
    for date,tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        one_year_temp.append(tobs_dict)
        
    print(f'Total result {len(one_year_temp)} rows')
    return jsonify(one_year_temp)

@app.route("/api/v1.0/start/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Dates from start date
    start_date = start
    
    TMIN = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date)
    TMAX = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date)
    TAVG = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date)

    given_start_temp=[{"TMIN": TMIN[0][0]},
                    {"TMAX": TMAX[0][0]},
                    {"TAVG": round(TAVG[0][0],0)} 
                        ]

    return jsonify(given_start_temp)

    session.close()

@app.route("/api/v1.0/start/end/<start>/<end>")
def start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Dates for query period
    start_date = start
    end_date = end

    TMIN = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date)
    TMAX = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date)
    TAVG = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date)

    given_start_temp=[{"TMIN": TMIN[0][0]},
                    {"TMAX": TMAX[0][0]},
                    {"TAVG": round(TAVG[0][0],0)} 
                        ]

    return jsonify(given_start_temp)

    session.close()


if __name__ == '__main__':
    app.run(debug=True)
