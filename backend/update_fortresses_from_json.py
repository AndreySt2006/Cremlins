"""Обновляет строки в таблице `fortresses` данными из
`frontend/query_kremlins.json`.

Сопоставление делаем по координатам (lon,lat) с небольшой толерантностью.
"""
import json
from pathlib import Path
from app.database import engine
from sqlalchemy import text

base = Path(__file__).resolve().parents[1]
local_path = base / 'frontend' / 'query_kremlins.json'

if not local_path.exists():
    raise FileNotFoundError(f"Expected data file not found: {local_path}")

with open(local_path, 'r', encoding='utf-8') as fh:
    data = json.load(fh)

# build mapping coord -> wikidataId
mapping = []
for it in data:
    coord = it.get('coord')
    if coord and coord.startswith('Point('):
        inner = coord.replace('Point(', '').replace(')', '')
        parts = inner.split()
        try:
            lon = float(parts[0])
            lat = float(parts[1])
        except Exception:
            continue
        mapping.append((lon, lat, it.get('wikidataId')))

with engine.begin() as conn:
    updated = 0
    for lon, lat, wid in mapping:
        if not wid:
            continue
        q = text("SELECT id, ST_X(location) AS lon, ST_Y(location) AS lat FROM fortresses")
        rows = conn.execute(q).mappings().all()
        target = None
        for r in rows:
            rl = r['lon']
            ra = r['lat']
            if rl is None or ra is None:
                continue
            if round(rl,5) == round(lon,5) and round(ra,5) == round(lat,5):
                target = r['id']
                break
        if target:
            uq = text("UPDATE fortresses SET wikidata_id = :wid WHERE id = :id")
            conn.execute(uq, {"wid": wid, "id": target})
            updated += 1

print(f'Обновлено записей с wikidata_id: {updated}')


