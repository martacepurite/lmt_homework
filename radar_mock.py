import requests
import random
import time
import json
import math
import numpy as np
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

MIN_HEADING_DEG = 0
MAX_HEADING_DEG = 360
MIN_SPEED_MS = 1
MAX_SPEED_MS = 2000
MIN_ALTITUDE_M = 5
# Lower than 200km so as not to pick up spacecraft (? unclear)
# MAX_ALTITUDE_M = 2000
MAX_ALTITUDE_M = 500

MIN_LATITUDE_GLOBAL = -90
MAX_LATITUDE_GLOBAL = 90

MIN_LONGITUDE_GLOBAL = -180
MAX_LONGITUDE_GLOBAL = 180

# each radar has 200km effective radius

RADAR_LAT_1 = 56.97475845607155
RADAR_LON_1 = 24.1670070219384

RADAR_LAT_2 = 56.516083346891044
RADAR_LON_2 = 21.0182217849017

RADAR_LAT_3 = 55.87409588616014
RADAR_LON_3 = 26.51864225209475

# Approximate conversion from lat/long deg to km
# Latitude: 1 deg = 110.574 km
# Longitude: 1 deg = 111.320 * cos(latitude) km

# Longitude
# 1km = 1deg/(cos(latitude) * 111.320)
# 200km = 200deg/(cos(latitude) * 111.320)

# Latitude
# 1km = 1deg/110.574km
# 1km = 0.0090437 deg/km
# 200km = 200deg/110.574km
# 200km = 1.80874 deg/km


path_radar_api = "http://127.0.0.1:8000/radar/"

# random.seed(10)

def calculate_radar_range(radar_lat, radar_lon):
    deg_200km = 1.80874
    latitude_200km_north = radar_lat + deg_200km
    latitude_200km_south = radar_lat - deg_200km

    longitude_200km_east = radar_lon + 200/(math.cos(math.radians(radar_lat)) * 111.320)
    longitude_200km_west = radar_lon - 200/(math.cos(math.radians(radar_lat)) * 111.320)

    return round(latitude_200km_north, 7), round(latitude_200km_south, 7), round(longitude_200km_east, 7), round(longitude_200km_west, 7)


def generate_random_radar_data():
    which_radar = random.randint(1, 3)

    radar_lat = 0
    radar_lon = 0

    if which_radar == 1:
        radar_lat = RADAR_LAT_1
        radar_lon = RADAR_LON_1
    elif which_radar == 2:
        radar_lat = RADAR_LAT_2
        radar_lon = RADAR_LON_2
    else:
        radar_lat = RADAR_LAT_3
        radar_lon = RADAR_LON_3

    lat_max, lat_min, lon_max, lon_min = calculate_radar_range(radar_lat, radar_lon)

    speed_ms = round(random.uniform(MIN_SPEED_MS, MAX_SPEED_MS), 7)
    altitude_m = round(random.uniform(MIN_ALTITUDE_M, MAX_ALTITUDE_M), 7)
    heading_deg = round(random.uniform(MIN_HEADING_DEG, MAX_HEADING_DEG), 7)
    latitude = round(random.uniform(lat_min, lat_max), 7)
    longitude = round(random.uniform(lon_min, lon_max), 7)
    report_time = round(time.time())

    data = {
        "speed_ms": speed_ms,
        "altitude_m": altitude_m,
        "heading_deg": heading_deg,
        "latitude": latitude,
        "longitude": longitude,
        "report_time": report_time
    }

    return data


actionable_radar_data = [
    {
        "speed_ms": 66.1375455, # Daugavpils only
        "altitude_m": 967.7105407,
        "heading_deg": 5.3396806,
        "latitude": 55.7387316,
        "longitude": 26.4628966,
        "report_time": 1771499951
    },
    {
        "speed_ms": 1993.1174281,
        "altitude_m": 93.889983,
        "heading_deg": 309.6579734,
        "latitude": 56.2473859,
        "longitude": 25.7603382,
        "report_time": 1771499951
    },
    {
        "speed_ms": 1795.9851297,
        "altitude_m": 1397.2513429,
        "heading_deg": 152.391817,
        "latitude": 57.0570019,
        "longitude": 23.6855625,
        "report_time": 1771501189
    },
    {
        "speed_ms": 1479.5428755,
        "altitude_m": 649.5084518,
        "heading_deg": 11.843851,
        "latitude": 55.8735191,
        "longitude": 26.8349929,
        "report_time": 1771501189
    },
    {
        "speed_ms": 400.2817357,
        "altitude_m": 1545.690476,
        "heading_deg": 286.9629606,
        "latitude": 57.04575,
        "longitude": 25.5451234,
        "report_time": 1771501189
    },
    {
        "speed_ms": 400.2817357, # Both Riga and Daugavpils
        "altitude_m": 200.690476,
        "heading_deg": 286.9629606,
        "latitude": 56.489357,
        "longitude": 25.368585,
        "report_time": 1771501189
    }

]
# 1 - Riga - dist < 100'000
# 2 - Liepaja - dist < 30'000
# 3 - Daugavp - dist < 100'000


N_THREATS = 15


if __name__ == '__main__':

    # for n in range(N_THREATS):

    #     d = generate_random_radar_data()
    #     r = requests.post(path_radar_api, json=d)

    #     print()
    #     if r.status_code == 200:
    #         print(json.dumps(d, indent=4))
    #         print(json.dumps(r.json(), indent=4))
    #     else:
    #         print(r.text)



    for d in actionable_radar_data:
        r = requests.post(path_radar_api, json=d)

        print()
        if r.status_code == 200:
            print(json.dumps(d, indent=4))
            print(json.dumps(r.json(), indent=4))
        else:
            print(r.text)



    # Plot bases
    # data_points = {"latitude": [RADAR_LAT_1, RADAR_LAT_2, RADAR_LAT_3],
    #                 "longitude": [RADAR_LON_1, RADAR_LON_2, RADAR_LON_3],
    #                 "type": ["base", "base", "base"],
    #                 "range": [200, 100, 100]}
    # df = pd.DataFrame(data=data_points)

    # for n in range(N_THREATS):

    #     d1 = generate_random_radar_data()
    #     threat = {"latitude": d1["latitude"], "longitude": d1["longitude"], "type": "threat", "range": 50}
    #     df.loc[len(df)] = threat

    # # threat = {"latitude": d1["latitude"], "longitude": d1["longitude"], "type": "threat"}

    # # df.loc[len(df)] = threat
    # colors=('#1e90ff','#ff8c00','#2e8b57', '#1e90ff','#fa9cff','#4f7b57')

    # fig = go.Figure(data=go.Scattergeo(
    #     lon = df['longitude'],
    #     lat = df['latitude'],
    #     text = df['type'],
    #     mode = 'markers',
    #     marker_color = colors,
    #     marker = dict(
    #         size = 8,
    #         opacity = 0.8,
    #         symbol = 'square',
    #     )))

    # # fig.update_layout()
    # fig.update_geos(fitbounds="locations", scope="europe", showcountries=True, lataxis_showgrid=True, lonaxis_showgrid=True, resolution=50)


    # fig = px.scatter_geo(df, color="type", lat="latitude", lon="longitude", scope="europe", center={'lat': RADAR_LAT_1, 'lon': RADAR_LON_1 }, size="range")
    # fig.show()

