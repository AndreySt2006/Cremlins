from sqlalchemy import Column, Integer, String, Text, Boolean
from geoalchemy2 import Geometry
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


class Kremlin(Base):
    __tablename__ = "fortresses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    location = Column(Geometry('POINT', srid=4326))
    description = Column(Text, nullable=True)
    foundation_year = Column(Integer, nullable=True)
    architectural_style = Column(String, nullable=True)
    image_url = Column(String, nullable=True)