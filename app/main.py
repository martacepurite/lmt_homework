from typing import Annotated, Union
from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlmodel import Session, SQLModel, create_engine, select
import os
from geopy import distance
import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import uuid
import uvicorn

from .definitions import AirDefenseSolution, Base, RadarMessage, Classification, Response, NoActionResponse


RADAR_LAT_1 = 56.97475845607155
RADAR_LON_1 = 24.1670070219384

RADAR_LAT_2 = 56.516083346891044
RADAR_LON_2 = 21.0182217849017

RADAR_LAT_3 = 55.87409588616014
RADAR_LON_3 = 26.51864225209475

TIME_DELTA = 5 # step for calculations, in seconds
MAX_TIME = 1000 # how far in time to calculate, in seconds

PLOT = os.getenv("PLOT", "browser")

if os.environ.get("PYTEST_VERSION") is not None:
    PLOT = "none"


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def add_initial_database_entries():

    airdef_drone = AirDefenseSolution(name="Interceptor drone", speed=80, range=3000, max_altitude=2000, price=10000, cost_type="unit")
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
def post_radar_message(message: RadarMessage, session: SessionDep) -> Union[Response, NoActionResponse]:
    classification = process_radar_data(message, session)

    if classification == Classification.CAUTION or classification == Classification.IGNORE:
        return NoActionResponse(message=classification.value)

    response = get_threat_response(message, session)

    if response == Classification.IMPOSSIBLE:
        return NoActionResponse(message=response.value)

    return response


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


def calculate_object_path(start_latitude, start_longitude, d_time, max_time, object_speed, heading_deg, info_text):
    # Vx = V0*cos(θ)
    # Vy = V0*sin(θ)
    theta = 90 - (heading_deg % 180) # angle relative to x axis
    target_velocity_x = object_speed * math.cos(math.radians(theta))
    target_velocity_y = object_speed * math.sin(math.radians(theta))
    # Calculate next positions of target
    # Calculate distance traveled in x and y directions
    r_earth = 6378000 # m
    object_path = []

    for time_s in range(0,max_time, d_time):
        dx = target_velocity_x * time_s
        dy = target_velocity_y * time_s
        # check for mistakes wrt units - radians
        new_latitude  = start_latitude + (dy / r_earth) * (180 / math.pi)
        new_longitude = start_longitude + (dx / r_earth) * (180 / math.pi) / math.cos(new_latitude * math.pi/180)
        next_targ_loc = {"latitude": new_latitude, "longitude": new_longitude, "type": "threat", "info": str(info_text), "t": time_s}
        object_path.append(next_targ_loc)
    
    return object_path


def get_threat_response(radar_message: RadarMessage, session: SessionDep):

    all_bases = session.exec(select(Base)).all()
    coords_target_vec = [radar_message.latitude, radar_message.longitude, radar_message.altitude_m]
    radar_data_dict = radar_message.model_dump()
    target_speed = radar_message.speed_ms
    target_altitude = radar_message.altitude_m
    # Get weapons in each base that have max alt to reach target

    possible_bases_weapons = []
    for b in all_bases:
        base_dict = b.model_dump()
        in_range_weapons = []
        for a in b.airdefense:
            if a.max_altitude >= target_altitude:
                in_range_weapons.append(a.model_dump())

        if len(in_range_weapons) > 0:
            base_dict["defense_systems"] = in_range_weapons
            possible_bases_weapons.append(base_dict)

    if len(possible_bases_weapons) < 1:
        return Classification.IMPOSSIBLE

    threat_path = calculate_object_path(coords_target_vec[0], coords_target_vec[1], TIME_DELTA, MAX_TIME, target_speed, radar_message.heading_deg, str(radar_data_dict))
    
    # Calculate coordinate of interception for each in range weapon in each base
    # Calculate cost for each option

    interceptor_paths = []
    response_options = []
    longest_interc_time = 0 # For plotting threat path (where to end it)

    # Iterate bases with possible weapons
    for base in possible_bases_weapons:
        base_lat = base["latitude"]
        base_lon = base["longitude"]
        # Iterate weapons in base
        for intercep in base["defense_systems"]:
            interception_coords = []
            interc_time_threat = 0
            coords_base = (base_lat, base_lon, 0)
            interception_cost = 0
            optimal_velocity_interc = math.inf
            closest_distance_to_base = math.inf

            for threat_coords in threat_path[1:]:
                coords_target_n = (threat_coords["latitude"], threat_coords["longitude"], radar_message.altitude_m)
                distance_2d = distance.distance(coords_base[:2], coords_target_n[:2]).m
                distance_3d = np.sqrt(distance_2d**2 + (coords_target_n[2] - coords_base[2])**2)

                if distance_3d < closest_distance_to_base:
                    if distance_3d/threat_coords["t"] <= intercep["speed"]:
                        closest_distance_to_base = distance_3d 
                        interc_time_threat = threat_coords["t"]
                        interception_coords = coords_target_n
                        if threat_coords["t"] > longest_interc_time:
                            longest_interc_time = threat_coords["t"]

            if closest_distance_to_base > intercep["range"]:
                continue

            optimal_velocity_interc = closest_distance_to_base/interc_time_threat

            if intercep["cost_type"] == "unit":
                interception_cost = intercep["price"]
            else:
                interception_cost = intercep["price"] * interc_time_threat

            response_details = {
                "response_id": len(response_options) + 1,
                "base_id": base["id"],
                "base_name": base["name"],
                "air_def_id": intercep["id"],
                "air_def_name": intercep["name"],
                "cost": interception_cost,
                "distance": closest_distance_to_base,
                "interc_time": interc_time_threat,
                "interc_lat": interception_coords[0],
                "interc_lon": interception_coords[1],
                "speed": optimal_velocity_interc
            }

            response_options.append(response_details)

            if PLOT != "none":
                # Path of interceptor
                # Calculate x, y, z components of interceptor velocity
                # Get difference between starting and ending coordinates and calculate speed
                base_intercep_coords_difference = np.array(interception_coords) - np.array(coords_base)
                # latitude/s   longitude/s   m/s !!!
                velocity_intercep_vector = base_intercep_coords_difference / interc_time_threat
                interceptor_path = []
                d_time_s = 0 
                while d_time_s <= interc_time_threat + TIME_DELTA * 3: # Plot paths a little past interception
                    d_lat = velocity_intercep_vector[0] * d_time_s
                    d_lon = velocity_intercep_vector[1] * d_time_s
                    new_latitude = coords_base[0] + d_lat
                    new_longitude = coords_base[1] + d_lon
                    next_interc_loc = {"latitude": new_latitude, "longitude": new_longitude, "type": intercep["name"], "info": str(intercep), "t": d_time_s}
                    interceptor_path.append(next_interc_loc)
                    d_time_s += TIME_DELTA

                interceptor_paths.append(interceptor_path)

    if len(response_options) < 1:
        return Classification.IMPOSSIBLE

    # Choose cheapest response option
    min_cost = math.inf
    chosen_resp = response_options[0]
    for resp in response_options:
        if resp["cost"] < min_cost:
            min_cost = resp["cost"]
            chosen_resp = resp
    
    if PLOT != "none":
        record_id = str(uuid.uuid4())[:8]
        if "record_id" in radar_data_dict.keys():
            record_id = radar_data_dict["record_id"]
        plot_paths(chosen_resp, threat_path, longest_interc_time, interceptor_paths, record_id)

    response = Response(base=str(chosen_resp["base_name"]), type=str(chosen_resp["air_def_name"]), latitude=chosen_resp["interc_lat"], longitude=chosen_resp["interc_lon"])

    return response


def plot_paths(chosen_resp, threat_path, longest_interc_time, interceptor_paths, record_id):
    data_points_bases = {"latitude": [RADAR_LAT_1, RADAR_LAT_2, RADAR_LAT_3],
                        "longitude": [RADAR_LON_1, RADAR_LON_2, RADAR_LON_3],
                        "type": ["base", "base", "base"],
                        "info": ["Riga", "Liepaja", "Daugavpils"],
                        "t": [0, 0, 0]
                        }
    df_bases = pd.DataFrame(data=data_points_bases)
    fig = go.Figure()
    # Plot base locations
    fig.add_trace(go.Scattergeo(
        lon = df_bases['longitude'],
        lat = df_bases['latitude'],
        text = df_bases['info'],
        mode = 'markers',
        name = "Base",
        marker = dict(
            size = 15,
            color = 'rgb(0, 255, 0)',
            line = dict(
                width = 3,
                color = 'rgba(68, 68, 68, 0)'
            )
    )))

    chosen_point_data = []
    pt = {"latitude": chosen_resp["interc_lat"], "longitude": chosen_resp["interc_lon"], "type": chosen_resp["air_def_name"], "info": str(chosen_resp), "t": chosen_resp["interc_time"]}
    chosen_point_data.append(pt)
    df_chosen_point = pd.DataFrame(data=chosen_point_data)

    fig.add_trace(go.Scattergeo(
        lon = df_chosen_point['longitude'],
        lat = df_chosen_point['latitude'],
        text = df_chosen_point['info'],
        name = "Interception point",
        mode = 'markers',
        marker = dict(
            size = 12,
            symbol = "x",
            line = dict(
                width = 3,
                color = 'rgba(68, 68, 68, 0)'
            )
    )))

    df_object_paths = pd.DataFrame(threat_path)

    # Plot line from start to end of relevant threat path
    longest_interc_time_index = df_object_paths.index[df_object_paths['t']==longest_interc_time].tolist()[0]
    if len(df_object_paths) > longest_interc_time_index + 1:
        longest_interc_time_index += 1

    fig.add_trace(
        go.Scattergeo(
            lon = df_object_paths['longitude'][0:longest_interc_time_index+1],
            lat = df_object_paths['latitude'][0:longest_interc_time_index+1],
            mode = 'lines',
            line = dict(width = 2,color = 'red'),
            text = df_object_paths['t'][0:longest_interc_time_index+1],
            name = "Threat"
        )
    )
    # Marker at the start of threat path
    fig.add_trace(
        go.Scattergeo(
            lon = [df_object_paths['longitude'][0]],
            lat = [df_object_paths['latitude'][0]],
            mode = 'markers',
            name = "Detection coordinate",
            marker=dict(
                size=10,
                color = 'rgb(255, 0, 0)',
            ),  
        )
    )
    # Interceptor paths
    for paths in interceptor_paths:
        df_interceptor = pd.DataFrame(paths)
        fig.add_trace(
            go.Scattergeo(
                lon = df_interceptor['longitude'],
                lat = df_interceptor['latitude'],
                mode = 'lines',
                line = dict(width = 2,color = 'blue'),
                text = df_interceptor['info']
            )
        )

    fig.update_geos(fitbounds="locations", scope="europe", showcountries=True, lataxis_showgrid=True, lonaxis_showgrid=True, resolution=50)
    fig.update_layout(hoverdistance=100)

    if PLOT == "browser":
        fig.show(renderer="browser")
    else:
        filename = "./plots/plot"

        if not os.path.exists("./plots"):
            os.makedirs("./plots")
        if PLOT == "html":
            filename = filename + "_" + str(record_id) + ".html"
            fig.write_html(filename)
        # if PLOT == "png":
        #     filename = filename + "_" + str(record_id) + ".png"
        #     fig.write_image(filename)
        # if PLOT == "jpeg":
        #     filename = filename + "_" + str(record_id) + ".jpeg"
        #     fig.write_image(filename)
        


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
