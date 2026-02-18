from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select
import sqlite3
from enum import Enum
from pydantic import BaseModel
import os
from geopy import distance
import math
import numpy as np
import json
import pandas as pd
import plotly.express as px

from .definitions import AirDefenseSolution, Base, RadarMessage, Classification, Response
RADAR_LAT_1 = 56.97475845607155
RADAR_LON_1 = 24.1670070219384

RADAR_LAT_2 = 56.516083346891044
RADAR_LON_2 = 21.0182217849017

RADAR_LAT_3 = 55.87409588616014
RADAR_LON_3 = 26.51864225209475


# from definitions import CostType, BaseAirDefenseLink, AirDefenseSolution, Base, RadarMessage

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def add_initial_database_entries():

    airdef_drone = AirDefenseSolution(name="Interceptor drone", speed=80, range=30000, max_altitude=2000, price=10000, cost_type="unit")
    airdef_jet = AirDefenseSolution(name="Fighter jet", speed=700, range=3500, max_altitude=15000, price=1000, cost_type="time")
    airdef_rocket= AirDefenseSolution(name="Rocket", speed=1500, range=100000, max_altitude=30000, price=300000, cost_type="unit")
    airdef_50cal = AirDefenseSolution(name="50Cal", speed=900, range=2000, max_altitude=2000, price=1, cost_type="unit")

    base_riga = Base(name="Riga", latitude=56.97475845607155, longitude=24.1670070219384, airdefense=[airdef_drone, airdef_jet, airdef_rocket, airdef_50cal])
    base_liepaja = Base(name="Liepaja", latitude=56.516083346891044, longitude=21.0182217849017, airdefense=[airdef_drone, airdef_50cal])
    base_daugavpils = Base(name="Daugavpils", latitude=55.87409588616014, longitude=26.51864225209475, airdefense=[airdef_drone, airdef_rocket, airdef_50cal])

    session = Session(engine)
    session.add(base_riga)
    session.add(base_liepaja)
    session.add(base_daugavpils)
    session.commit()
    session.close()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    add_initial_database_entries()

@app.on_event("shutdown")
def on_shutdown():
    if os.path.exists("database.db"):
        os.remove("database.db")


@app.post("/radar/")
def create_radar_message(message: RadarMessage, session: SessionDep):
    classification = process_radar_data(message, session)

    if classification == Classification.CAUTION or classification == Classification.IGNORE:
        return classification

    response = get_threat_response(message, session)
    return response 

@app.post("/bases/")
def create_base(base: Base, session: SessionDep) -> Base:
    session.add(base)
    session.commit()
    session.refresh(base)
    return base

@app.get("/bases/")
def read_bases(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Base]:
    bases = session.exec(select(Base).offset(offset).limit(limit)).all()
    return bases

@app.get("/airdefense/")
def read_airdefense(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[AirDefenseSolution]:
    airdefensesolutions = session.exec(select(AirDefenseSolution).offset(offset).limit(limit)).all()
    return airdefensesolutions

@app.get("/bases/{base_id}")
def read_base(base_id: int, session: SessionDep) -> Base:
    base = session.get(Base, base_id)
    if not base:
        raise HTTPException(status_code=404, detail="base not found")
    return base

@app.delete("/bases/{base_id}")
def delete_base(base_id: int, session: SessionDep):
    base = session.get(Base, base_id)
    if not base:
        raise HTTPException(status_code=404, detail="base not found")
    session.delete(base)
    session.commit()
    return {"ok": True}

# {
#   "speed_ms": 0,
#   "altitude_m": 0,
#   "heading_deg": 0,
#   "latitude": 0,
#   "longitude": 0,
#   "report_time": 0
# }
def process_radar_data(radar_message: RadarMessage, session: SessionDep):

    # Add error handling
    radar_dict = radar_message.model_dump()

    if radar_dict["speed_ms"] > 50:
        return Classification.THREAT

    if radar_dict["speed_ms"] < 15:
        return Classification.IGNORE

    if radar_dict["altitude_m"] < 200:
        return Classification.IGNORE

    if radar_dict["speed_ms"] <= 50:
        return Classification.CAUTION

    return Classification.THREAT


# Calculate coordinate where target will be intercepted
def get_interception_coords(radar_message: RadarMessage, airdef_speed):
    pass

        
# Target needs to be within range 
# Calculate cost
# Prefer cheapest 

def get_threat_response(radar_message: RadarMessage, session: SessionDep):
    print()
    print(radar_message)
    print()

    all_bases = session.exec(select(Base)).all()

    # Get target distance from each base
    coords_target = (radar_message.latitude, radar_message.longitude, radar_message.altitude_m)
    coords_target_vec = [radar_message.latitude, radar_message.longitude, radar_message.altitude_m]
    bases_distances = {}
    bases_distances_coord_vectors = {}
    
    for b in all_bases:
        coords_base = (b.latitude, b.longitude, 0)
        distance_2d = distance.distance(coords_base[:2], coords_target[:2]).m
        distance_3d = np.sqrt(distance_2d**2 + (coords_target[2] - coords_base[2])**2)
        bases_distances[b.id] = round(distance_3d, 7)

        coords_base_vec = [b.latitude, b.longitude, 0]
        # dist_vec = np.subtract(coords_target_vec, coords_base_vec)
        dist_vec = np.absolute(np.array(coords_target_vec) - np.array(coords_base_vec))
        bases_distances_coord_vectors[b.id] = dist_vec


    # print(bases_distances_coord_vectors)


    # print(coords_target)
    # print()
    # print(bases_distances)

    min_distance = bases_distances[1]
    min_distance_base_id = 1

    for d in bases_distances.keys():
        if bases_distances[d] < min_distance:
            min_distance = bases_distances[d]
            min_distance_base_id = d

    # print(min_distance_base_id)
    # print(min_distance)

    # Get weapons in each base that have range to reach target
    possible_bases_weapons = []
    print()
    for b in all_bases:

        base_dict = b.model_dump()
        in_range_weapons = []
        for a in b.airdefense:
            if (a.range >= bases_distances[b.id]) and (a.max_altitude >= radar_message.altitude_m):
                in_range_weapons.append(a.model_dump())
        
        if len(in_range_weapons) > 0:
            base_dict["defense_systems"] = in_range_weapons
            possible_bases_weapons.append(base_dict)


    # Calculate path of target
    # Calculate displacement each second
    # Assume target altitude is constant
    # Assume speeds are constant
    # Ignore gravity etc
    # Interceptor is launched at 45 degree angle?

    # d = vt
    # d0 = 0
    # d1 = speed * 1

    target_displacement = []
    target_speed = radar_message.speed_ms
    target_altitude = radar_message.altitude_m

    for i in range(0,10):
        target_displacement.append(round(target_speed * i, 7))


    print(target_displacement)
    
    # Calculate displacement each second for launched interceptor
    # Calculate distance between target and base each second
    # Need to recalculate coordinates each second

    # Distance interceptor has travelled = Distance from target to base
    # Distance interceptor has travelled = time * speed_interc
    # Distance from target to base = D_timezero +(-) t * (speed at which it is moving towards base (component of velocity vector that is in the direction of base)) (this is not the right way)

    # Calculate distances componentwise separately for each axis
    # Calculate x and y components of target velocity, needs heading degrees
    # need to account for sign/direction, check later
    # Vx = V0*cos(θ)
    # Vy = V0*sin(θ)

    theta = 90 - (radar_message.heading_deg % 180) # angle relative to x axis
    target_velocity_x = target_speed * math.cos(math.radians(theta))
    target_velocity_y = target_speed * math.sin(math.radians(theta))
    # print("target_velocity_x:")
    # print(target_velocity_x)
    # print("target_velocity_y:")
    # print(target_velocity_y)

    # Calculate next positions of target
    # Calculate distance traveled in x and y directions

    r_earth = 6378000 # m
    targ_lat = coords_target_vec[0]
    targ_lon = coords_target_vec[1]
    threat_path = []

    # for time_s in range(1,100):
    for time_s in range(1,5000,50):
        dx = target_velocity_x * time_s
        dy = target_velocity_y * time_s
        # check for mistakes wrt units - radians
        new_latitude  = targ_lat + (dy / r_earth) * (180 / math.pi)
        new_longitude = targ_lon + (dx / r_earth) * (180 / math.pi) / math.cos(targ_lat * math.pi/180)
        next_targ_loc = {"latitude": new_latitude, "longitude": new_longitude, "type": "threat", "t": time_s}
        threat_path.append(next_targ_loc)
    
    # for base in possible_bases_weapons:
    #     print(json.dumps(base, indent=4))

    base_1_lat = possible_bases_weapons[0]["latitude"]
    base_1_lon = possible_bases_weapons[0]["longitude"]
    intercep_1 = possible_bases_weapons[0]["defense_systems"][0]
    print(json.dumps(intercep_1, indent=4))
    # Calculate coordinate of interception: 
    # Calculate time to reach coordinate on threat path for each point on path
    # Check if time to reach is equal or close to time of threat path point
    # if it is the same or close, that is the solution coordinate, where target and airdef will meet

    closest_time = math.inf
    interception_coords = []
    intercep_info = ""

    for threat_coords in threat_path:
        coords_target_n = (threat_coords["latitude"], threat_coords["longitude"], radar_message.altitude_m)
        # print(coords_target_n)
        coords_base = (base_1_lat, base_1_lon, 0)
        distance_2d = distance.distance(coords_base[:2], coords_target_n[:2]).m
        distance_3d = np.sqrt(distance_2d**2 + (coords_target_n[2] - coords_base[2])**2)
        # print(distance_3d)
        time_airdef = round(distance_3d/intercep_1["speed"], 4)
        time_diff = np.absolute(time_airdef - threat_coords["t"])
        print("time_airdef: " + str(time_airdef) + ", time_threat: " + str(threat_coords["t"]) + " ,difference: " + str(time_diff))

        if time_diff < closest_time:
            closest_time = time_diff
            interception_coords = coords_target_n
            intercep_info = "time_airdef: " + str(time_airdef) + ", time_threat: " + str(threat_coords["t"]) + " ,difference: " + str(time_diff)

    
    print(interception_coords)
    print(intercep_info)

    # Calculate coordinate of interception for each in range weapon in each base
    # Calculate cost for each option

    # Plot
    data_points = {"latitude": [RADAR_LAT_1, RADAR_LAT_2, RADAR_LAT_3],
                    "longitude": [RADAR_LON_1, RADAR_LON_2, RADAR_LON_3],
                    "type": ["base", "base", "base"],
                    "t": [0, 0, 0]
                    }
    df = pd.DataFrame(data=data_points)

    for p in threat_path:
        df.loc[len(df)] = p

    fig = px.scatter_geo(df, color="type", lat="latitude", lon="longitude", scope="europe", center={'lat': RADAR_LAT_1, 'lon': RADAR_LON_1 }, hover_name="t")
    fig.show()


    all_air_defense = session.exec(select(AirDefenseSolution)).all()
    chosen_base = list(all_bases)[0]
    chosen_weapon = list(all_air_defense)[0]
    response = Response(base=str(chosen_base.name), type=str(chosen_weapon.name), latitude=50.2, longitude=21.1)

    return response
