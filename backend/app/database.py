"""
База данных — PostgreSQL через SQLAlchemy ORM.

СТАТУС: НЕ ИСПОЛЬЗУЕТСЯ — бэкенд сейчас работает на mock-данных (routers/).
        Подключить, когда будем переходить к реальной БД.

ЧТО НУЖНО ДЛЯ РАБОТЫ:
  1. PostgreSQL + расширение PostGIS (для геометрии в models.py).
     Установить PostGIS: CREATE EXTENSION postgis;
  2. Вынести DATABASE_URL в переменную окружения (сейчас credentials захардкожены — это небезопасно):
       DATABASE_URL = os.environ["DATABASE_URL"]
     или использовать python-dotenv с .env файлом.
  3. Запустить миграции (Alembic или Base.metadata.create_all(engine)).

КАК ПОДКЛЮЧИТЬ К РОУТЕРАМ:
  from .database import SessionLocal
  # Dependency для FastAPI:
  def get_db():
      db = SessionLocal()
      try: yield db
      finally: db.close()
  # В роутере: db: Session = Depends(get_db)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+psycopg2://andreystewart:050607@localhost:5432/kremls_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
