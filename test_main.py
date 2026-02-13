import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool 

from .main import app, get_session
from .definitions import Base, AirDefenseSolution, CostType


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_read_bases(session: Session, client: TestClient):

    airdef_drone = AirDefenseSolution(name="Interceptor drone", speed=80, range=30000, max_altitude=2000, price=10000, cost_type=CostType.UNIT)
    airdef_jet = AirDefenseSolution(name="Fighter jet", speed=700, range=3500, max_altitude=15000, price=1000, cost_type=CostType.TIME)
    airdef_rocket= AirDefenseSolution(name="Rocket", speed=1500, range=100000, max_altitude=30000, price=300000, cost_type=CostType.UNIT)
    airdef_50cal = AirDefenseSolution(name="50Cal", speed=900, range=2000, max_altitude=2000, price=1, cost_type=CostType.UNIT)

    base_riga = Base(name="Riga", latitude=56.97475845607155, longitude=24.1670070219384, airdefense=[airdef_drone, airdef_jet, airdef_rocket, airdef_50cal])
    base_liepaja = Base(name="Liepaja", latitude=56.516083346891044, longitude=21.0182217849017, airdefense=[airdef_drone, airdef_50cal])
    base_daugavpils = Base(name="Daugavpils", latitude=55.87409588616014, longitude=26.51864225209475, airdefense=[airdef_drone, airdef_rocket, airdef_50cal])

    session.add(base_riga)
    session.add(base_liepaja)
    session.add(base_daugavpils)
    session.commit()

    response = client.get("/bases/")
    data = response.json()

    assert response.status_code == 200

    assert len(data) == 3
    assert data[0]["name"] == base_riga.name
    assert data[0]["latitude"] == base_riga.latitude
    assert data[0]["longitude"] == base_riga.longitude



# def test_create_hero(client: TestClient):
#     response = client.post(
#         "/heroes/", json={"name": "Deadpond", "secret_name": "Dive Wilson"}
#     )
#     data = response.json()

#     assert response.status_code == 200
#     assert data["name"] == "Deadpond"
#     assert data["secret_name"] == "Dive Wilson"
#     assert data["age"] is None
#     assert data["id"] is not None

# def test_create_hero_incomplete(client: TestClient):
#     # No secret_name
#     response = client.post("/heroes/", json={"name": "Deadpond"})
#     assert response.status_code == 422


# def test_create_hero_invalid(client: TestClient):
#     # secret_name has an invalid type
#     response = client.post(
#         "/heroes/",
#         json={
#             "name": "Deadpond",
#             "secret_name": {"message": "Do you wanna know my secret identity?"},
#         },
#     )
#     assert response.status_code == 422


# def test_read_heroes(session: Session, client: TestClient):
#     hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
#     hero_2 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)
#     session.add(hero_1)
#     session.add(hero_2)
#     session.commit()

#     response = client.get("/heroes/")
#     data = response.json()

#     assert response.status_code == 200

#     assert len(data) == 2
#     assert data[0]["name"] == hero_1.name
#     assert data[0]["secret_name"] == hero_1.secret_name
#     assert data[0]["age"] == hero_1.age
#     assert data[0]["id"] == hero_1.id
#     assert data[1]["name"] == hero_2.name
#     assert data[1]["secret_name"] == hero_2.secret_name
#     assert data[1]["age"] == hero_2.age
#     assert data[1]["id"] == hero_2.id


# def test_read_hero(session: Session, client: TestClient):
#     hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
#     session.add(hero_1)
#     session.commit()

#     response = client.get(f"/heroes/{hero_1.id}")
#     data = response.json()

#     assert response.status_code == 200
#     assert data["name"] == hero_1.name
#     assert data["secret_name"] == hero_1.secret_name
#     assert data["age"] == hero_1.age
#     assert data["id"] == hero_1.id


# def test_update_hero(session: Session, client: TestClient):
#     hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
#     session.add(hero_1)
#     session.commit()

#     response = client.patch(f"/heroes/{hero_1.id}", json={"name": "Deadpuddle"})
#     data = response.json()

#     assert response.status_code == 200
#     assert data["name"] == "Deadpuddle"
#     assert data["secret_name"] == "Dive Wilson"
#     assert data["age"] is None
#     assert data["id"] == hero_1.id


# def test_delete_hero(session: Session, client: TestClient):
#     hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
#     session.add(hero_1)
#     session.commit()

#     response = client.delete(f"/heroes/{hero_1.id}")

#     hero_in_db = session.get(Hero, hero_1.id)

#     assert response.status_code == 200

#     assert hero_in_db is None
