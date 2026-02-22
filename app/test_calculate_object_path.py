import pytest
from .main import calculate_object_path
from .definitions import Base, AirDefenseSolution

def test_calculate_object_path_constant():

    path = calculate_object_path(start_latitude=45.32421, start_longitude=23.32423, d_time=100, max_time=1000, object_speed=1000, heading_deg=300, info_text="info")

    d_lat_ref = path[1]["latitude"] - path[0]["latitude"]
    d_lon_ref = path[1]["longitude"] - path[0]["longitude"]

    for i in range(1,len(path)-1):
        lon1 = path[i]["longitude"]
        lon2 = path[i+1]["longitude"]
        lat1 = path[i]["latitude"]
        lat2 = path[i+1]["latitude"]
        print(path[i])
        print(lon2-lon1)
        print(lat2-lat1)
        ## TODO FIX
        # assert (lon2-lon1) == pytest.approx(d_lon_ref, rel=1e-3)
        # assert (lat2-lat1) == pytest.approx(d_lat_ref, rel=1e-3)

def test_calculate_object_path_heading_east():
    path = calculate_object_path(start_latitude=45.32421, start_longitude=23.32423, d_time=100, max_time=1000, object_speed=1000, heading_deg=90, info_text="info")

    for i in range(len(path)-1):
        lat1 = path[i]["latitude"]
        lat2 = path[i+1]["latitude"]
        assert (lat2-lat1) == pytest.approx(0)

def test_calculate_object_path_heading_west():
    path = calculate_object_path(start_latitude=45.32421, start_longitude=23.32423, d_time=100, max_time=1000, object_speed=1000, heading_deg=270, info_text="info")

    for i in range(len(path)-1):
        lat1 = path[i]["latitude"]
        lat2 = path[i+1]["latitude"]
        assert (lat2-lat1) == pytest.approx(0)

def test_calculate_object_path_heading_north():
    path = calculate_object_path(start_latitude=45.32421, start_longitude=23.32423, d_time=100, max_time=1000, object_speed=1000, heading_deg=360, info_text="info")

    for i in range(len(path)-1):
        lon1 = path[i]["longitude"]
        lon2 = path[i+1]["longitude"]
        assert (lon2-lon1) == pytest.approx(0)

def test_calculate_object_path_heading_south():
    path = calculate_object_path(start_latitude=45.32421, start_longitude=23.32423, d_time=100, max_time=1000, object_speed=1000, heading_deg=180, info_text="info")

    for i in range(len(path)-1):
        lon1 = path[i]["longitude"]
        lon2 = path[i+1]["longitude"]
        assert (lon2-lon1) == pytest.approx(0)