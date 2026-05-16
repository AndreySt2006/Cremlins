from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from .database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Fortress(Base):
    __tablename__ = "fortresses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    location = Column(Geometry('POINT', srid=4326))
    description = Column(Text, nullable=True)
    foundation_year = Column(Integer, nullable=True)
    architectural_style = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    comments_count = Column(Integer, default=0)
    # Дополнительные поля, которые могут понадобиться фронтенду
    city = Column(String, nullable=True)
    wikipedia_url = Column(String, nullable=True)
    wikidata_id = Column(String, nullable=True)


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    kremlin_id = Column(Integer, ForeignKey("fortresses.id"), nullable=False, index=True)
    author_id = Column(Integer, nullable=False)
    author_name = Column(String, nullable=False)
    author_avatar_url = Column(String, nullable=True)
    text = Column(Text, nullable=False)
    image_urls = Column(JSON, nullable=False, server_default='[]')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationship to fortress (table name is fortresses / class Fortress)
    fortress = relationship("Fortress", backref="comments")


# Совместимость: в других модулях ожидается имя "Kremlin"
# Чтобы не переименовывать всю кодовую базу — оставим алиас.
Kremlin = Fortress
