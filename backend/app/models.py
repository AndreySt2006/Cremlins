"""
SQLAlchemy ORM-модели — описание таблиц в PostgreSQL.

СТАТУС: НЕ ИСПОЛЬЗУЕТСЯ — бэкенд сейчас работает на mock-данных (routers/).
        Подключить вместе с database.py при переходе к реальной БД.

ЗАВИСИМОСТИ:
  - geoalchemy2  (pip: geoalchemy2) — для поля Geometry в модели Kremlin.
  - PostGIS-расширение в PostgreSQL (см. database.py).

РАСХОЖДЕНИЯ С ТЕКУЩИМИ MOCK-СХЕМАМИ (schemas.py):
  - User не имеет поля username и avatarUrl — нужно добавить при создании таблицы.
  - Kremlin не имеет полей city, yearBuilt, wikipediaUrl, wikidataId, images,
    commentsCount — все они есть в schemas.py и используются фронтендом.
    Добавить соответствующие Column-поля перед первой миграцией.
  - Kremlin.tablename = "fortresses" — при желании можно переименовать в "kremlins".

СОЗДАНИЕ ТАБЛИЦ (без Alembic, для быстрого старта):
  from app.database import engine
  from app.models import Base
  Base.metadata.create_all(bind=engine)
"""

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
