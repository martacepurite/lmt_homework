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

from .definitions import AirDefenseSolution, Base, CostType, RadarMessage, Classification, Response

# from definitions import CostType, BaseAirDefenseLink, AirDefenseSolution, Base, RadarMessage

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def add_initial_database_entries():

    airdef_drone = AirDefenseSolution(name="Interceptor drone", speed=80, range=30000, max_altitude=2000, price=10000, cost_type=CostType.UNIT)
    airdef_jet = AirDefenseSolution(name="Fighter jet", speed=700, range=3500, max_altitude=15000, price=1000, cost_type=CostType.TIME)
    airdef_rocket= AirDefenseSolution(name="Rocket", speed=1500, range=100000, max_altitude=30000, price=300000, cost_type=CostType.UNIT)
    airdef_50cal = AirDefenseSolution(name="50Cal", speed=900, range=2000, max_altitude=2000, price=1, cost_type=CostType.UNIT)

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
    all_bases = session.exec(select(Base)).all()


    print()
    print(radar_message)
    print()

    # Get target distance from each base
    coords_target = (radar_message.latitude, radar_message.longitude, radar_message.altitude_m)
    bases_distances = {}
    
    for b in all_bases:
        coords_base = (b.latitude, b.longitude, 0)
        distance_2d = distance.distance(coords_base[:2], coords_target[:2]).m
        distance_3d = np.sqrt(distance_2d**2 + (coords_target[2] - coords_base[2])**2)
        bases_distances[b.id] = round(distance_3d, 7)

    print(coords_target)
    print()
    print(bases_distances)

    min_distance = bases_distances[1]
    min_distance_base_id = 1

    for d in bases_distances.keys():
        if bases_distances[d] < min_distance:
            min_distance = bases_distances[d]
            min_distance_base_id = d

    print(min_distance_base_id)
    print(min_distance)

    # Get weapons in each base that have range to reach target
    possible_bases_weapons = []
    print()
    for b in all_bases:

        base_dict = b.model_dump()
        in_range_weapons = []
        for a in b.airdefense:
            if a.range >= bases_distances[b.id]:
                in_range_weapons.append(a.model_dump())
        
        if len(in_range_weapons) > 0:
            base_dict["defense_systems"] = in_range_weapons
            possible_bases_weapons.append(base_dict)

    
    
    # print(json.dumps(possible_bases_weapons, indent=4))
        



    # Calculate coordinate of interception for each in range weapon in each base


    # Calculate cost for each option

    all_air_defense = session.exec(select(AirDefenseSolution)).all()

    chosen_base = list(all_bases)[0]
    chosen_weapon = list(all_air_defense)[0]


    response = Response(base=str(chosen_base.name), type=str(chosen_weapon.name), latitude=50.2, longitude=21.1)

    return response
