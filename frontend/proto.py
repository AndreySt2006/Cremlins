"""
Russian Kremlins Interactive Guide (Streamlit proto / MVP)

MVP goals (from frontend/roadmap_streamlit.md):
- Interactive map with markers for each Kremlin (id, name, lat, lon)
- Clicking a marker navigates to a Kremlin detail page
- Detail page shows basic info and photo gallery; optional sections are hidden if missing
- Simple "Routes" feature: user creates a checklist/list of Kremlins (no navigation yet)

Notes:
- No backend yet. Data source is `frontend/query_kremlins.json` (Wikidata export). Fallback to a small seed list.
- Uses OpenStreetMap tiles (works in Russia without VPN).

Run:
  pip install -r requirements.txt
  streamlit run frontend/proto.py
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlsplit, urlunsplit

import folium
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("Russian Kremlins Interactive Guide")

# ---------------------------
# 1) Data: use only `query_kremlins.json` (Wikidata export). Fallback to a small seed list.
# ---------------------------
DEFAULT_KREMLINS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "Astrakhan Kremlin",
        "lat": 46.3494,
        "lon": 48.0322,
        "city": "Astrakhan",
        "description": "",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/9/9c/Astrakhan_Kremlin_(262683297).jpeg",
            "https://upload.wikimedia.org/wikipedia/commons/5/56/Astrakhan_Kremlin_walls.jpg",
        ],
        "comments": [],
    },
    {
        "id": 2,
        "name": "Kazan Kremlin",
        "lat": 55.7992,
        "lon": 49.1056,
        "city": "Kazan",
        "description": "",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/a/ac/Kazan_Kremlin_as_seen_from_hatchlbaus.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/9/98/Kazan_Kremlin_Aqueduct.jpg",
        ],
        "comments": [],
    },
    {
        "id": 3,
        "name": "Kolomna Kremlin",
        "lat": 55.0830,
        "lon": 38.7830,
        "city": "Kolomna",
        "description": "",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/1/1f/Kolomna_Kremlin.JPG",
            "https://upload.wikimedia.org/wikipedia/commons/a/a3/Kremlin_Churches1.jpg",
        ],
        "comments": [],
    },
    {
        "id": 4,
        "name": "Moscow Kremlin",
        "lat": 55.7517,
        "lon": 37.6178,
        "city": "Moscow",
        "description": "",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/8/83/Moscow_Kremlin.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/5/5d/Moscow_Kremlin_at_night.jpg",
        ],
        "comments": [],
    },
    {
        "id": 5,
        "name": "Nizhny Novgorod Kremlin",
        "lat": 56.3275,
        "lon": 44.0007,
        "city": "Nizhny Novgorod",
        "description": "",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/e/e3/%D0%9A%D1%80%D0%B5%D0%BC%D0%BB%D1%8C_%D0%9D%D0%B8%D0%B6%D0%BD%D0%B5%D0%B3%D0%BE_%D0%BD%D0%B0%D0%B7%D0%B0%D0%BC_%D0%B2_%D1%88%D1%82%D0%BE%D1%80%D0%BC%D0%B5.JPG",
            "https://upload.wikimedia.org/wikipedia/commons/2/2d/Нижегородский_кремль.jpg",
        ],
        "comments": [],
    },
    {
        "id": 6,
        "name": "Novgorod Kremlin",
        "lat": 58.5192,
        "lon": 31.2720,
        "city": "Veliky Novgorod",
        "description": "",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/9/97/Novgorod_Kremlin.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/3/36/%D0%9D%D0%BE%D0%B2%D0%B3%D0%BE%D1%80%D0%BE%D0%B4_%D0%9A%D1%80%D0%B5%D0%BC%D0%BB%D1%8C.jpg",
        ],
        "comments": [],
    },
    {
        "id": 7,
        "name": "Pskov Kremlin",
        "lat": 57.8170,
        "lon": 28.3330,
        "city": "Pskov",
        "description": "",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/2/27/Pskov_Kremlin.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/6/6a/%D0%9F%D1%81%D0%BA%D0%BE%D0%B2_%D0%9A%D1%80%D0%B5%D0%BC%D0%BB%D1%8C.jpg",
        ],
        "comments": [],
    },
    {
        "id": 8,
        "name": "Rostov Kremlin",
        "lat": 57.1994,
        "lon": 39.4247,
        "city": "Rostov",
        "description": "",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/5/5e/Rostov_Kremlin_9674.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/d/d1/%D0%A0%D0%BE%D1%81%D1%82%D0%BE%D0%B2_%D0%9A%D1%80%D0%B5%D0%BC%D0%BB%D1%8C.jpg",
        ],
        "comments": [],
    },
    {
        "id": 9,
        "name": "Smolensk Kremlin",
        "lat": 54.7828,
        "lon": 32.0453,
        "city": "Smolensk",
        "description": "",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/8/8a/Smolensk_Kremlin_-_10.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/3/30/Smolensk_kremlin.jpg",
        ],
        "comments": [],
    },
    {
        "id": 10,
        "name": "Tobolsk Kremlin",
        "lat": 58.2000,
        "lon": 68.2670,
        "city": "Tobolsk",
        "description": "",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/5/58/Tobolsk_Kremlin_and_Old_Water_Tower.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/4/4e/Tobolsk_kremlin.jpg",
        ],
        "comments": [],
    },
    {
        "id": 11,
        "name": "Tula Kremlin",
        "lat": 54.1953,
        "lon": 37.6200,
        "city": "Tula",
        "description": "",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/4/4a/Tula_Kremlin_view.JPG",
            "https://upload.wikimedia.org/wikipedia/commons/b/b9/%D0%A2%D1%83%D0%BB%D0%B0_%D0%BA%D1%80%D0%B5%D0%BC%D0%BB%D1%8C.jpg",
        ],
        "comments": [],
    },
    {
        "id": 12,
        "name": "Zaraysk Kremlin",
        "lat": 54.7567,
        "lon": 38.8692,
        "city": "Zaraysk",
        "description": "",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/3/3a/Zaraisk_Kremlin_walls.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/d/d2/%D0%97%D0%B0%D1%80%D0%B0%D0%B9%D1%81%D0%BA_%D0%BA%D1%80%D0%B5%D0%BC%D0%BB%D1%8C.jpg",
        ],
        "comments": [],
    },
]


def _safe_image_url(url: str) -> str:
    """
    Some Wikimedia URLs contain Cyrillic characters; encode the path so
    Streamlit/fetch doesn't drop the second image.
    """
    try:
        parts = urlsplit(url)
        safe_path = quote(parts.path)
        return urlunsplit(
            (parts.scheme, parts.netloc, safe_path, parts.query, parts.fragment)
        )
    except Exception:
        return url


def _parse_wkt_point(wkt: str) -> Optional[Dict[str, float]]:
    # "Point(lon lat)"
    if not isinstance(wkt, str):
        return None
    if not wkt.startswith("Point(") or not wkt.endswith(")"):
        return None
    body = wkt[len("Point(") : -1].strip()
    parts = body.split()
    if len(parts) != 2:
        return None
    try:
        lon = float(parts[0])
        lat = float(parts[1])
        return {"lon": lon, "lat": lat}
    except Exception:
        return None


def _normalize_kremlin(raw: Dict[str, Any], fallback_id: int) -> Dict[str, Any]:
    kremlin_id = raw.get("id", fallback_id)
    name = raw.get("name") or raw.get("title") or f"Kremlin #{kremlin_id}"
    lat = raw.get("lat")
    lon = raw.get("lon")
    city = raw.get("city") or ""
    description = raw.get("description") or ""
    images = raw.get("images") or []
    comments = raw.get("comments") or []

    return {
        "id": int(kremlin_id),
        "name": str(name),
        "lat": float(lat),
        "lon": float(lon),
        "city": str(city),
        "description": str(description),
        "images": [_safe_image_url(u) for u in images],
        "comments": list(comments),
    }


def load_kremlins() -> List[Dict[str, Any]]:
    query_path = "frontend/query_kremlins.json"
    try:
        with open(query_path, "r", encoding="utf-8") as f:
            rows = json.load(f)
        out: List[Dict[str, Any]] = []
        for idx, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                continue
            label = row.get("itemLabel") or row.get("name") or row.get("label")
            wkt = row.get("coord")
            wikidata_id = row.get("wikidataId") or ""
            point = _parse_wkt_point(wkt)
            if not label or not point:
                continue

            # Use numeric part of Q-id as stable integer id
            kremlin_id = idx
            if (
                isinstance(wikidata_id, str)
                and wikidata_id.startswith("Q")
                and wikidata_id[1:].isdigit()
            ):
                kremlin_id = int(wikidata_id[1:])

            out.append(
                _normalize_kremlin(
                    {
                        "id": kremlin_id,
                        "name": label,
                        "lat": point["lat"],
                        "lon": point["lon"],
                        "city": "",
                        "description": "",
                        "images": [],
                        "comments": [],
                    },
                    fallback_id=kremlin_id,
                )
            )

        if out:
            out.sort(key=lambda x: x["name"])
            return out
    except Exception:
        pass

    return [
        _normalize_kremlin(k, fallback_id=i + 1) for i, k in enumerate(DEFAULT_KREMLINS)
    ]


kremlins = load_kremlins()
kremlins_by_id = {k["id"]: k for k in kremlins}
kremlins_by_name_lower = {k["name"].lower(): k for k in kremlins}
valid_tooltips = {k["name"] for k in kremlins}

# ---------------------------
# 2) Routing via query params:
#    - If ?id=<id> → show detail page for that Kremlin
#    - Otherwise show map
# ---------------------------
kremlin_id_param = st.query_params.get("id")


def find_kremlin_by_id(kremlin_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not kremlin_id:
        return None
    try:
        kremlin_id_int = int(kremlin_id)
    except Exception:
        return None
    return kremlins_by_id.get(kremlin_id_int)


def _ensure_routes_state() -> None:
    if "route_items" not in st.session_state:
        st.session_state.route_items = []
    if "route_delete_confirm" not in st.session_state:
        st.session_state.route_delete_confirm = None


def _route_add(k_id: int) -> None:
    _ensure_routes_state()
    if any(item["id"] == k_id for item in st.session_state.route_items):
        return
    st.session_state.route_items.append({"id": k_id, "checked": False})


def _route_remove(k_id: int) -> None:
    _ensure_routes_state()
    st.session_state.route_items = [
        x for x in st.session_state.route_items if x["id"] != k_id
    ]


def _go_to_map() -> None:
    st.query_params.clear()
    st.rerun()


def _go_to_kremlin(k_id: int) -> None:
    st.query_params["id"] = str(k_id)
    st.rerun()


_ensure_routes_state()
if "user_photos" not in st.session_state:
    st.session_state.user_photos = {}  # {kremlin_id: [urls]}

if kremlin_id_param:
    # DETAIL PAGE
    kremlin = find_kremlin_by_id(kremlin_id_param)
    if not kremlin:
        st.error(f"Kremlin id '{kremlin_id_param}' not found in local dataset.")
        if st.button("Back to map"):
            _go_to_map()
        st.stop()

    st.header(kremlin["name"])
    if kremlin.get("city"):
        st.write(f"**City:** {kremlin['city']}")
    st.write(f"**Coordinates:** {kremlin['lat']}, {kremlin['lon']}")
    st.caption("Source: frontend/query_kremlins.json (Wikidata export).")
    st.markdown("---")

    # Description (optional)
    if kremlin.get("description"):
        st.write(kremlin["description"])
        st.markdown("---")

    # Merge base images + user-added session images
    session_imgs = st.session_state.user_photos.get(kremlin["id"], [])
    merged_images = list(kremlin.get("images") or []) + session_imgs

    # Photo (representative) + gallery
    if merged_images:
        first = merged_images[0]
        st.image(
            first, use_column_width=True, caption=f"{kremlin['name']} (representative)"
        )
    else:
        st.info("No images available for this Kremlin yet.")

    st.markdown("### Photo gallery (up to 20 images)")
    images = merged_images[:20]
    if images:
        cols = st.columns(3)
        for i, img in enumerate(images):
            col = cols[i % 3]
            with col:
                col.image(img, use_column_width=True)
    else:
        st.write("No photos found.")

    with st.expander("Add a photo URL (will require account later)"):
        new_url = st.text_input("Photo URL", key=f"add_photo_{kremlin['id']}")
        if st.button("Add photo", key=f"add_photo_btn_{kremlin['id']}"):
            if new_url:
                safe = _safe_image_url(new_url)
                st.session_state.user_photos.setdefault(kremlin["id"], []).append(safe)
                st.success("Added. (Note: future versions will require an account.)")
                st.rerun()
            else:
                st.warning("Please paste a URL.")

    st.markdown("---")
    # Comments (read-only for now)
    st.subheader("Comments")
    comments = kremlin.get("comments") or []
    if comments:
        for c in comments:
            if isinstance(c, dict):
                author = c.get("author") or "anonymous"
                text = c.get("text") or ""
                st.write(f"- **{author}**: {text}")
            else:
                st.write(f"- {c}")
    else:
        st.caption("No comments yet. (Writing comments will require an account later.)")

    st.markdown("---")
    st.subheader("Actions")
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("Back to map", use_container_width=True):
            _go_to_map()
    with c2:
        if any(item["id"] == kremlin["id"] for item in st.session_state.route_items):
            if st.button("Remove from route", use_container_width=True):
                _route_remove(kremlin["id"])
                st.rerun()
        else:
            if st.button("Add to route", use_container_width=True):
                _route_add(kremlin["id"])
                st.rerun()

    st.caption(
        "Account features (favorites/visited/comments/uploads) will be added after backend is connected."
    )
    st.markdown("[Back to top](#russian-kremlins-interactive-guide)")

else:
    # MAP PAGE
    st.markdown("## Map — click a Kremlin marker to open its detail page.")

    with st.sidebar:
        st.subheader("Search")
        search = st.text_input("Search by name", value="")
        st.divider()
        st.subheader("Route (checklist)")
        if st.session_state.route_items:
            for item in st.session_state.route_items:
                rid = item["id"]
                rk = kremlins_by_id.get(rid)
                if not rk:
                    continue
                cols = st.columns([1, 6, 2])
                with cols[0]:
                    checked = st.checkbox(
                        "",
                        value=item["checked"],
                        key=f"route_check_{rid}",
                    )
                    item["checked"] = checked
                with cols[1]:
                    label = rk["name"]
                    if checked:
                        label = f"~~{label}~~"
                    cols[1].markdown(label)
                    if cols[1].button("Open", key=f"route_open_{rid}"):
                        _go_to_kremlin(rid)
                with cols[2]:
                    if st.button("Remove", key=f"route_remove_{rid}"):
                        st.session_state.route_delete_confirm = rid

                if st.session_state.route_delete_confirm == rid:
                    st.warning("Remove this item?")
                    if st.button("Confirm remove", key=f"route_confirm_{rid}"):
                        _route_remove(rid)
                        st.session_state.route_delete_confirm = None
                        st.rerun()
                    if st.button("Cancel", key=f"route_cancel_{rid}"):
                        st.session_state.route_delete_confirm = None
                        st.rerun()
        else:
            st.caption("Add Kremlins from a detail page to build a travel plan.")

        if st.session_state.route_items:
            if st.button("Clear route"):
                st.session_state.route_items = []
                st.session_state.route_delete_confirm = None
                st.rerun()

    # Create folium map centered on Russia
    map_center = [61.5240, 105.3188]
    m = folium.Map(
        location=map_center,
        zoom_start=4,
        tiles="OpenStreetMap",
        max_bounds=True,
    )
    # Constrain view roughly to Russia
    m.fit_bounds([[41.0, 19.0], [82.0, 180.0]])

    # Add markers with a consistent "fortress" icon (normal marker icon, not thumbnails).
    filtered = kremlins
    if search.strip():
        s = search.strip().lower()
        filtered = [k for k in kremlins if s in k["name"].lower()]

    for k in filtered:
        name = k["name"]
        lat = k["lat"]
        lon = k["lon"]

        icon = folium.Icon(color="red", icon="fort-awesome", prefix="fa")
        folium.Marker(
            location=[lat, lon],
            tooltip=name,
            popup=folium.Popup(name, max_width=300),
            icon=icon,
        ).add_to(m)

    st_map_data = st_folium(m, width=1000, height=700)

    # Only navigate when user clicked a known marker (avoid accidental background map clicks).
    if st_map_data:
        clicked_tooltip = st_map_data.get("last_object_clicked_tooltip")
        if clicked_tooltip and clicked_tooltip in valid_tooltips:
            clicked = kremlins_by_name_lower.get(clicked_tooltip.lower())
            if clicked:
                _go_to_kremlin(clicked["id"])
