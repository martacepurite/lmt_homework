import requests
import random
import time
import json
import math
import os
import uuid
import argparse

parser = argparse.ArgumentParser()

MIN_HEADING_DEG = 0
MAX_HEADING_DEG = 360
MIN_SPEED_MS = 1
MAX_SPEED_MS = 2000
MIN_ALTITUDE_M = 5
MAX_ALTITUDE_M = 2000

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


path_radar_api  = os.getenv("PATH_RADAR_API", "http://127.0.0.1:8000/radar/")

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
    report_time = int(time.time())
    record_id = str(uuid.uuid4())[:8]

    data = {
        "speed_ms": speed_ms,
        "altitude_m": altitude_m,
        "heading_deg": heading_deg,
        "latitude": latitude,
        "longitude": longitude,
        "report_time": report_time,
        "record_id": record_id
    }

    return data


actionable_radar_data = [
    {
        "speed_ms": 66.1375455, # Daugavpils only
        "altitude_m": 967.7105407,
        "heading_deg": 5.3396806,
        "latitude": 55.7387316,
        "longitude": 26.4628966,
        "report_time": 1771499951,
        "record_id": "bb76924e"
    },
    {
        "speed_ms": 1993.1174281,
        "altitude_m": 93.889983,
        "heading_deg": 309.6579734,
        "latitude": 56.2473859,
        "longitude": 25.7603382,
        "report_time": 1771499951,
        "record_id": "00c52183"
    },
    {
        "speed_ms": 1795.9851297,
        "altitude_m": 1397.2513429,
        "heading_deg": 152.391817,
        "latitude": 57.0570019,
        "longitude": 23.6855625,
        "report_time": 1771501189,
        "record_id": "28c037eb"
    },
    {
        "speed_ms": 400.2817357, # Both Riga and Daugavpils
        "altitude_m": 200.690476,
        "heading_deg": 286.9629606,
        "latitude": 56.489357,
        "longitude": 25.368585,
        "report_time": 1771501189,
        "record_id": "b214e984"
    }
]

if __name__ == '__main__':

    parser.add_argument("-p", "--prepared", action="store_true", help="Use prepared radar data  in radar_mock.py instead of generating new data")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print sent radar data")
    parser.add_argument("-n", "--ndata", type=int, default=10, help="Number of radar data requests to generate and send")

    args = parser.parse_args()

    responses = []
    radar_data = []

    if args.prepared:
        for d in actionable_radar_data:
            r = requests.post(path_radar_api, json=d)
            if args.verbose:
                radar_data.append(d)
            if r.status_code == 200:
                responses.append(r.json())
            else:
                responses.append(r.text)
        
    if not args.prepared:
        for n in range(args.ndata):
            d = generate_random_radar_data()
            if args.verbose:
                radar_data.append(d)
            r = requests.post(path_radar_api, json=d)
            if r.status_code == 200:
                responses.append(r.json())
            else:
                responses.append(r.text)


    if args.verbose:
        for i in range(len(responses)):
            print("Request data (" + str(i) + "):")
            print(json.dumps(radar_data[i], indent=4))
            print("Response (" + str(i) + "):")
            print(json.dumps(responses[i], indent=4))
            print()

    if not args.verbose:
        for r in responses:
            print(json.dumps(r, indent=4))
