## 1) Backend (FastAPI) — responsibilities + how Streamlit/React connect

### 1.1 Goals of the backend

- Provide a **stable JSON contract** so Streamlit and React can use the same API.
- Centralize:
  - Kremlin metadata (name, coords, city/region)
  - photos (source + user uploads)
  - comments
  - history layers (optional)
  - user state later (visited/favorites/routes)

### 1.2 Required API (stable response shapes)

From `frontend/roadmap_streamlit.md`:

- **GET** `/api/kremlins`

  - Returns a list of Kremlins for map and search.
  - Shape:
    - `id`, `name`, `lat`, `lon`, `city`, `has_history_layers`

- **GET** `/api/kremlins/{id}`
  - Returns the full Kremlin detail page.
  - Shape:
    - `id`, `name`, `description`
    - `coordinates: { lat, lon }`
    - `photos: [{ id, url, author }]`
    - `comments: [{ id, text, author }]`
    - `history_layers: [{ period, description, map_overlay_url }]` (optional)

### 1.3 Data/model requirements (backend side)

- **Kremlin**

  - `id` (integer; ideally derived from Wikidata Q-id numeric part for stability)
  - `name`
  - `lat`, `lon`
  - optional: `city`, `region`
  - optional: `description`
  - optional: `has_history_layers`

- **Photos**

  - store `url`, `author/source`, `license`, `source_url`
  - allow both “official sources” (Commons/Wikipedia) and user uploads later

- **Comments**

  - `text`, `author`, timestamps
  - read-only for anonymous users; write requires auth later

- **History layers (optional)**
  - period metadata + source + license

### 1.4 Auth (later, when backend is ready)

We are **skipping accounts now** in the Streamlit MVP, but backend should support:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/me`

Account is required only for:

- adding comments
- uploading photos
- favorites / visited list

### 1.5 How Streamlit connects (near-future)

From `frontend/backend_integration.md`:

- FastAPI: `http://127.0.0.1:8000`
- Streamlit: `http://localhost:8501`
- Streamlit should call backend using `requests` / `httpx` and cache results:
  - `st.cache_data(ttl=60)` for list/detail endpoints

Streamlit does **server-side HTTP**, so CORS is not usually an issue.

### 1.6 How React connects (later)

- React will call the API from the browser, so FastAPI must enable CORS:
  - allow `http://localhost:5173` (dev) and prod domain

---

## 2) Frontend — Streamlit prototype (what exists + what’s next)

### 2.1 Current Streamlit MVP (already implemented)

In `frontend/proto.py`:

- **Data source**

  - Uses **only** `frontend/query_kremlins.json` (Wikidata export).

- **Interactive map**

  - OpenStreetMap tiles.
  - “Kremlin” markers with a consistent fortress icon.
  - Clicking a marker opens the detail page for that specific Kremlin (`?id=...`).

- **Detail pages**

  - Basic info (name + coordinates)
  - Photo gallery (currently mostly empty because `query_kremlins.json` doesn’t contain photos yet)
  - “Add photo URL” (works now, but note says this will require an account later)
  - Comments section placeholder (read-only)
  - “Back to top” link

- **Routes (simple checklist)**
  - Add/remove Kremlin from a checklist (route)
  - Newly added items start unchecked
  - Checking an item visually crosses it out
  - Removing an item requires confirmation

### 2.2 Streamlit MVP — next features to implement

#### Data quality + map clarity

- Add/derive **city/region** for each Kremlin (prefer backend later; for now could be a local enrichment step).
- Show only relevant regions/cities (filter noise) for a “clean map”.
- Improve “Russia only” focus:
  - keep constrained bounds
  - optionally dim outside area (needs extra Leaflet/folium overlay logic; may be better in React)
- Also provide boundaries for Kremlins (from overpass-turbo), make sure that each point in each border is just one of points that connects a chain into actual border.

#### Kremlin pages

- Add a **mini-map** on the detail page centered on the Kremlin.
- Move “Back to map” and “Back to top” to the **top** of the page (UX).
- Add a “manual photos list” per Kremlin (local file or backend later) to make pages interesting.
- Add information about each Kremlin from wiki and other websites so that every page is a little history book about certain Kremlin.

#### Photos (current plan)

- Keep “Add photo URL” working for now.
- Later: replace it with an authenticated upload flow when backend is connected.

#### Output / export

- Export the user route/checklist to a file (e.g. **Markdown**):
  - list of Kremlin names + links/ids

#### Deferred / TODO (explicitly not now)

- Accounts/visited/favorites in Streamlit (wait for backend).
- Historical layers UI (wait until we have data + decide format).

---

## 3) React app roadmap (migration plan)

Tech stack (target):

- React + TypeScript
- Zustand (client state)
- React Query (server state)
- Tailwind CSS
- Ant Design (prebuilt components)
- Map: OpenStreetMap (via Leaflet.js, same as Streamlit uses folium → OpenStreetMap)

### 3.1 Principles

- Prioritize **features and data clarity** over fancy UI.
- Keep API shapes identical to backend contracts.
- Use **OpenStreetMap** for both Streamlit (folium) and React (Leaflet.js) — same map provider, same tiles, consistent UX.

### 3.2 Pages (minimal)

- **MapPage**

  - OpenStreetMap map (via Leaflet.js, same tiles as Streamlit)
  - markers for Kremlins
  - search/filter
  - click marker → navigate to detail route

- **KremlinPage**

  - load detail by id
  - photos gallery
  - comments
  - optional history section (hidden if empty)

- **RoutePage** (or sidebar panel)
  - checklist of selected Kremlins
  - export to Markdown

### 3.3 Data flow

- React Query:
  - `useQuery(['kremlins'], fetchKremlins)`
  - `useQuery(['kremlin', id], fetchKremlinDetail)`
- Zustand:
  - route/checklist state (selected ids + checked state)
  - later: auth token/user state

### 3.4 Milestones

- **Milestone A (React MVP, anonymous)**

  - MapPage + KremlinPage
  - route checklist
  - photos display from backend

- **Milestone B (Accounts + write actions)**

  - login/register
  - add comment
  - upload photo
  - favorites/visited

- **Milestone C (History layers)**
  - timeline/buttons
  - overlay rendering (Leaflet.js layer/overlay on OpenStreetMap)
  - source/license display
