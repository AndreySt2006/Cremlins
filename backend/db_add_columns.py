"""
Простой "миграционный" скрипт — добавляет недостающие колонки в таблицу `fortresses`.
"""
from sqlalchemy import text
from app.database import engine

queries = [
    "ALTER TABLE fortresses ADD COLUMN IF NOT EXISTS city TEXT;",
    "ALTER TABLE fortresses ADD COLUMN IF NOT EXISTS foundation_year INTEGER;",
    "ALTER TABLE fortresses ADD COLUMN IF NOT EXISTS wikipedia_url TEXT;",
    "ALTER TABLE fortresses ADD COLUMN IF NOT EXISTS wikidata_id TEXT;",
    "ALTER TABLE fortresses ADD COLUMN IF NOT EXISTS image_url TEXT;",
    "ALTER TABLE fortresses ADD COLUMN IF NOT EXISTS comments_count INTEGER DEFAULT 0;",
    "CREATE INDEX IF NOT EXISTS idx_fortresses_wikidata_id ON fortresses (wikidata_id);",
]

with engine.begin() as conn:
    for q in queries:
        conn.execute(text(q))

print('Миграция: добавлены/проверены колонки для fortresses')

