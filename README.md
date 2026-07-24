# CampusWay

An interactive geospatial web app built with Python and Streamlit that renders university campuses, pedestrian pathways, building footprints, and facilities using live OpenStreetMap (OSM) vector data.

---

## Why I Built This

When incoming freshmen or visitors arrive on a college campus for orientation or the first week of classes, finding specific buildings or walking routes is surprisingly frustrating. 

Standard navigation apps like Google Maps or Apple Maps are designed primarily for driving. They prioritize vehicular roads and often show campus grounds as a blank gray or green patch, completely skipping pedestrian footpaths, inner courtyards, and distinct building outlines. Official university maps, on the other hand, are usually static PDFs that are hard to read on a phone and can't be searched interactively.

I built CampusWay to solve this. You type in any university or college name, and the app queries spatial vector data to build a custom interactive map showing where students actually walk and where buildings and facilities are located.

---

## How It Works Under the Hood

1. **Geocoding & Boundary Resolution:** The search term goes to the Nominatim geocoding API to resolve the campus polygon boundary.
2. **Vector Data Extraction:** Once we have the campus boundary geometry, the app uses `OSMnx` to fetch raw vector data from OpenStreetMap across four spatial layers:
   - Campus Buildings (`building=True`)
   - Pedestrian Footpaths (`highway=footway, path, pedestrian, steps`)
   - Internal Roads & Service Routes (`highway=service, residential, etc.`)
   - Specialized Facilities (`amenity=library, food_court, cafe` and `leisure=sports_centre, fitness_centre`)
3. **Data Deduplication & Cleaning:** Overlapping building geometries are filtered out before map compilation.
4. **Interactive Map Rendering:** Layers are stylized and rendered on top of a clean CartoDB Positron base map using `leafmap` and `folium`.

---

## Engineering Bugs and Challenges I Fixed

Building this app required handling several quirks with geospatial data and Streamlit's execution model:

### 1. Stopping Nominatim API Rate-Limit Bans (HTTP 429)
OpenStreetMap enforces a strict policy of no more than 1 request per second for its free Nominatim service. Because Streamlit re-runs the entire Python script whenever a user toggles a sidebar checkbox or clicks a button, rapid clicks caused the app to hit the API multiple times a second, leading to HTTP 429 errors or temporary IP blocks.

* **Fix:** I wrote a `throttleNominatim()` function using `st.session_state` to track timestamps across re-renders. It calculates the time elapsed since the last API request and forces a short `time.sleep()` if the gap is under 1.1 seconds.

### 2. Eliminating Overlapping Polygon Visual Artifacts
OpenStreetMap frequently double-tags structures. For instance, a campus library might be tagged as both `building=yes` in the buildings layer and `amenity=library` in the facilities layer. Rendering both layers directly resulted in dark, muddy overlapping shapes.

* **Fix:** I wrote a `stripDuplicateBuildings()` helper function. It extracts the raw `osmid` set from the facilities GeoDataFrame and strips matching IDs out of the main buildings GeoDataFrame *before* converting the shapes into GeoJSON features for map rendering.

### 3. Caching Geospatial Data in Streamlit
`GeoPandas` GeoDataFrames are complex Python objects that are difficult to cache directly in Streamlit without memory leaks or serialization errors. Re-fetching full vector sets on every map interaction made the app painfully slow.

* **Fix:** I converted campus boundary geometries into WKT (Well-Known Text) strings. Passing plain text WKT strings into `@st.cache_data` allowed Streamlit to cache raw OSM responses for 6–24 hours, making map toggles instant without repeating network calls.

---

## Tech Stack

- **Language:** Python 3.10+
- **Frontend & Web Framework:** Streamlit
- **Geospatial Processing:** `OSMnx`, `GeoPandas`, `Shapely`, `Requests`
- **Mapping & Visualization:** `leafmap`, `folium`
- **Data Sources:** OpenStreetMap, Nominatim Search API

---

## Running Locally

1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR-USERNAME/CampusWay.git](https://github.com/YOUR-USERNAME/CampusWay.git)
   cd CampusWay
