from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
import sqlite3
from enum import Enum


class CostType(Enum):
    UNIT = "Cost per unit (single use)"
    TIME = "Cost per unit of time (minutes)"


class Base(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str 
    latitude: float
    longitude: float

class AirDefenseSolution(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str 
    speed: int
    range: int
    max_altitude: int
    price: int
    cost_type: CostType

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def add_initial_database_entries():
    base_1 = Base(name="Riga", latitude=56.97475845607155, longitude=24.1670070219384)
    base_2 = Base(name="Liepaja", latitude=56.516083346891044, longitude=21.0182217849017)
    base_3 = Base(name="Daugavpils", latitude=55.87409588616014, longitude=26.51864225209475)

    airdef_1 = AirDefenseSolution(name="Interceptor drone", speed=80, range=30000, max_altitude=2000, price=10000, cost_type=CostType.UNIT)
    airdef_2 = AirDefenseSolution(name="Fighter jet", speed=700, range=3500, max_altitude=15000, price=1000, cost_type=CostType.TIME)
    airdef_3 = AirDefenseSolution(name="Rocket", speed=1500, range=100000, max_altitude=30000, price=300000, cost_type=CostType.UNIT)
    airdef_4 = AirDefenseSolution(name="50Cal", speed=900, range=2000, max_altitude=2000, price=1, cost_type=CostType.UNIT)

    session = Session(engine)

    session.add(base_1)
    session.add(base_2)
    session.add(base_3)

    session.add(airdef_1)
    session.add(airdef_2)
    session.add(airdef_3)
    session.add(airdef_4)

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
