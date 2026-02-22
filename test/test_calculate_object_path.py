import pytest
from ..app.main import calculate_object_path
from ..app.definitions import Base, AirDefenseSolution

def test_calculate_object_path_heading_northwest():

    d_time = 100
    max_time = 1000
    start_latitude=45.32421
    start_longitude=23.32423

    path = calculate_object_path(start_latitude=start_latitude, start_longitude=start_longitude, d_time=d_time, max_time=max_time, object_speed=1000, heading_deg=300, info_text="info")

    assert len(path) == max_time / d_time

    path_elem = path[len(path)-1]

    assert path_elem["latitude"] < start_latitude
    assert path_elem["longitude"] > start_longitude


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