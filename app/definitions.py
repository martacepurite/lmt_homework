from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select
import sqlite3
from enum import Enum
from pydantic import BaseModel


class Classification(Enum):
    THREAT = "Threat"
    CAUTION = "Caution"
    IGNORE = "Not a threat or caution"

class BaseAirDefenseLink(SQLModel, table=True):
    base_id: int | None = Field(default=None, foreign_key="base.id", primary_key=True)
    airdefensesolution_id: int | None = Field(default=None, foreign_key="airdefensesolution.id", primary_key=True)

class AirDefenseSolution(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str 
    speed: int
    range: int
    max_altitude: int
    price: int
    cost_type: str

    bases: list["Base"] = Relationship(back_populates="airdefense", link_model=BaseAirDefenseLink)

class Base(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str 
    latitude: float
    longitude: float

    airdefense: list[AirDefenseSolution] = Relationship(back_populates="bases", link_model=BaseAirDefenseLink)
    
class RadarMessage(BaseModel):
    speed_ms: float
    altitude_m: float
    heading_deg: float
    latitude: float
    longitude: float
    report_time: float

class Response(BaseModel):
    base: str
    type: str
    latitude: float
    longitude: float
