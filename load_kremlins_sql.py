import requests
import re
from sqlalchemy import text

from app.database import Base, engine
import app.models  # важно для регистрации моделей

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

FAST_QUERY = """
SELECT DISTINCT ?item ?itemLabel ?coord ?image ?desc ?article WHERE {
  ?item wdt:P17 wd:Q159.
  ?item wdt:P625 ?coord.
  ?item rdfs:label ?label.
  FILTER(CONTAINS(LCASE(?label), "кремль"))
  FILTER(LANG(?label) = "ru")
  OPTIONAL { ?item wdt:P18 ?image. }
  OPTIONAL { ?item schema:description ?desc. FILTER(LANG(?desc) = "ru") }
  OPTIONAL { ?article schema:about ?item; schema:isPartOf <https://ru.wikipedia.org/>. }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru". }
}
LIMIT 1000
"""

TRASH_WORDS = [
    "атака", "беспилотник", "завод", "церковь",
    "собор", "здание", "пожар", "дворец", "гора"
]


def parse_point(point_str: str):
    if not point_str:
        return None, None

    m = re.search(r"([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)", point_str)
    if not m:
        return None, None

    lon = float(m.group(1))
    lat = float(m.group(2))
    return lon, lat


def sync_data():
    url = "https://query.wikidata.org/sparql"
    headers = {
        "User-Agent": "CremlinsOfRussia/1.0",
        "Accept": "application/sparql-results+json"
    }

    try:
        # SPARQL query may take time; increase timeout to be safe
        r = requests.get(url, params={"query": FAST_QUERY}, headers=headers, timeout=120)
        r.raise_for_status()
        raw_items = r.json()["results"]["bindings"]
        print(f"Получено из сети: {len(raw_items)} записей.")
    except Exception as e:
        print("Ошибка сети:", e)
        return

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE fortresses RESTART IDENTITY CASCADE;"))

        added = 0

        for row in raw_items:
            name = row.get("itemLabel", {}).get("value")
            coord = row.get("coord", {}).get("value")

            if not name or not coord:
                continue

            name_lower = name.lower()
            if any(w in name_lower for w in TRASH_WORDS):
                continue

            lon, lat = parse_point(coord)
            if lon is None or lat is None:
                continue

            clean_name = name.split("(")[0].strip()

            desc_val = row.get("desc") or None
            description = desc_val.get("value") if isinstance(desc_val, dict) else None

            img_val = row.get("image") or None
            image_url = img_val.get("value") if isinstance(img_val, dict) else None
            if not image_url:
                image_url = "https://placehold.co/600x400?text=Kremlin"
            else:
                if image_url.startswith('http://'):
                    image_url = 'https://' + image_url[len('http://'):]

            article_val = row.get("article") or None
            wikipedia_url = article_val.get("value") if isinstance(article_val, dict) else None
            if wikipedia_url and wikipedia_url.startswith('http://'):
                wikipedia_url = 'https://' + wikipedia_url[len('http://'):]

            if not description and wikipedia_url:
                try:
                    if '/wiki/' in wikipedia_url:
                        title = wikipedia_url.rsplit('/wiki/', 1)[1]
                        wiki_api = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{title}"
                        rh = requests.get(wiki_api, headers={'User-Agent': 'Cremlins/1.0'}, timeout=10)
                        if rh.status_code == 200:
                            j = rh.json()
                            desc = j.get('extract') or j.get('description')
                            if desc:
                                description = desc
                except Exception:
                    # ignore fetch errors — we'll keep None or the placeholder
                    pass

            # Wikidata id string (e.g. Q5110)
            wikidata_id = None
            item_val = row.get("item") or None
            if isinstance(item_val, dict):
                # item value is like 'http://www.wikidata.org/entity/Q5110'
                it = item_val.get("value", "")
                wikidata_id = it.rsplit('/', 1)[-1] if '/' in it else None

            q = text("""
                INSERT INTO fortresses (
                    name,
                    location,
                    description,
                    image_url,
                    foundation_year,
                    city,
                    wikipedia_url,
                    wikidata_id,
                    comments_count
                )
                VALUES (
                    :name,
                    ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
                    :description,
                    :image_url,
                    :foundation_year,
                    :city,
                    :wikipedia_url,
                    :wikidata_id,
                    0
                )
            """)

            conn.execute(q, {
                "name": clean_name,
                "lon": lon,
                "lat": lat,
                "description": description,
                "image_url": image_url,
                "foundation_year": None,
                "city": None,
                "wikipedia_url": wikipedia_url,
                "wikidata_id": wikidata_id,
            })

            added += 1

        print(f"Добавлено в базу: {added} кремлей.")


if __name__ == "__main__":
    sync_data()