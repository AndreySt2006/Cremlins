import requests
import psycopg2
import time

DB_PARAMS = {
    "dbname": "kremls_db",
    "user": "andreystewart",
    "password": "050607",
    "host": "localhost",
    "port": "5432"
}

FAST_QUERY = """
SELECT DISTINCT ?itemLabel ?coord WHERE {
  ?item wdt:P17 wd:Q159.       
  ?item wdt:P625 ?coord.      
  ?item rdfs:label ?label.
  FILTER(CONTAINS(LCASE(?label), "кремль"))
  FILTER(LANG(?label) = "ru")
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru". }
}
LIMIT 1000
"""

TRASH_WORDS = ["атака", "беспилотник", "завод", "церковь", "собор", "здание", "пожар", "дворец"]


def sync_data():
    url = "https://query.wikidata.org/sparql"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/sparql-results+json"
    }

    try:
        r = requests.get(url, params={'query': FAST_QUERY}, headers=headers, timeout=300)
        r.raise_for_status()
        raw_items = r.json()['results']['bindings']
        print(f"Получено из сети: {len(raw_items)} записей.")
    except Exception as e:
        print(f"Ошибка связи: {e}")
        return

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE fortresses;")

        added = 0
        for row in raw_items:
            name = row['itemLabel']['value']
            name_lower = name.lower()
            if any(trash in name_lower for trash in TRASH_WORDS):
                continue
            clean_name = name.split('(')[0].strip()
            coord_str = row['coord']['value']
            p = coord_str.replace("Point(", "").replace(")", "").split(" ")
            lon, lat = float(p[0]), float(p[1])
            cur.execute("""
                        INSERT INTO fortresses (name, location)
                        VALUES (%s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                        """, (clean_name, lon, lat))
            added += 1
        conn.commit()
        cur.close()
        conn.close()
        print(f"--- УСПЕХ! ---")
        print(f"После очистки в базу добавлено: {added} настоящих кремлей.")

    except Exception as e:
        print(f"Ошибка базы: {e}")


if __name__ == "__main__":
    sync_data()