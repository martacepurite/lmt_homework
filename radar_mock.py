import requests
import random
import time
import json

MIN_HEADING_DEG = 0
MAX_HEADING_DEG = 360
MIN_SPEED_MS = 1
MAX_SPEED_MS = 2000
MIN_ALTITUDE_M = 5
MAX_ALTITUDE_M = 2000

MIN_LATITUDE_GLOBAL = -90
MAX_LATITUDE_GLOBAL = 90

MIN_LATITUDE_LOCAL = 54
MAX_LATITUDE_LOCAL = 58

MIN_LONGITUDE_GLOBAL = -180
MAX_LONGITUDE_GLOBAL = 180

MIN_LONGITUDE_LOCAL = 20
MAX_LONGITUDE_LOCAL = 30

path_radar_api = "http://127.0.0.1:8000/radar/"

random.seed(10)

def generate_random_radar_data():
    speed_ms = random.uniform(MIN_SPEED_MS, MAX_SPEED_MS)
    altitude_m = random.uniform(MIN_ALTITUDE_M, MAX_ALTITUDE_M)
    heading_deg = random.uniform(MIN_HEADING_DEG, MAX_HEADING_DEG)
    latitude = random.uniform(MIN_LATITUDE_LOCAL, MAX_LATITUDE_LOCAL)
    longitude = random.uniform(MIN_LONGITUDE_LOCAL, MAX_LONGITUDE_LOCAL)
    report_time = time.time()

    data = {
        "speed_ms": speed_ms,
        "altitude_m": altitude_m,
        "heading_deg": heading_deg,
        "latitude": latitude,
        "longitude": longitude,
        "report_time": report_time
    }

    return data




if __name__ == '__main__':

    d1 = generate_random_radar_data()

    print(json.dumps(d1, indent=4))

    r = requests.post(path_radar_api, json=d1)

    if r.status_code == 200:
        print(json.dumps(r.json(), indent=4))
    else:
        print(r.text)

