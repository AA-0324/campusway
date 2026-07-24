import streamlit as st

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

import time
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape
from folium import plugins as folium_plugins
import leafmap.foliumap as leafmap
import osmnx as ox


def getIds(gdf):
    if gdf is None or gdf.empty:
        return set()
    try:
        if isinstance(gdf.index, pd.MultiIndex):
            if "osmid" in (gdf.index.names or []):
                return set(gdf.index.get_level_values("osmid"))
            return set(x[-1] if isinstance(x, tuple) else x for x in gdf.index)
        if "osmid" in gdf.columns:
            return set(gdf["osmid"])
    except Exception:
        pass
    return set()


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

campus_tags = {
    "buildings": {"building": True},
    "walkways": {"highway": ["footway", "path", "pedestrian", "steps"]},
    "roads": {"highway": ["service", "residential", "unclassified", "living_street"]},
    "facilities": {"amenity": ["library", "food_court", "cafe"], "leisure": ["sports_centre", "fitness_centre"]}
}

layer_labels = {
    "buildings": "Campus Buildings",
    "walkways": "Pedestrian Paths",
    "roads": "Roads & Service Routes",
    "facilities": "Specialized Facilities"
}

def styleFor(color, fill, opacity, weight):
    s = {"color": color, "fillColor": fill, "fillOpacity": opacity, "weight": weight, "opacity": 0.9}
    return lambda feat: s

campusStyles = {
    "buildings": styleFor("#1f77b4", "#1f77b4", 0.45, 1.0),
    "walkways": styleFor("#2ca02c", "#2ca02c", 0.0, 2.0),
    "roads": styleFor("#7f7f7f", "#7f7f7f", 0.0, 1.5),
    "facilities": styleFor("#d62728", "#d62728", 0.7, 1.5),
}

req_headers = {"User-Agent": "global-campus-navigator/1.0 (streamlit-app)"}
RATE_LIMIT_GAP = 1.1


@st.cache_resource
def initOsmnx():
    ox.settings.use_cache = True
    ox.settings.log_console = False
    return True


def throttleNominatim():
    t_last = st.session_state.get("nom_last", 0.0)
    gap = RATE_LIMIT_GAP - (time.monotonic() - t_last)
    if gap > 0:
        time.sleep(gap)
    st.session_state["nom_last"] = time.monotonic()


initOsmnx()


# Filtering sets to prevent geocoder from mistaking cities or parks for university campuses
NOT_CAMPUS = {"leisure", "shop", "tourism", "highway", "natural", "boundary"}

EDU_TAG_PAIRS = {
    ("amenity", "university"),
    ("amenity", "college"),
    ("amenity", "school"),
    ("amenity", "research_institute"),
    ("landuse", "education")
}

campusNameHints = ("university", "college", "institute of technology", "polytechnic", "academy", "ecole", "universidad", "universita")


def looksLikeCampus(nominatimResult):
    # Heuristic check to see if a search result is an educational polygon or random landmark
    pair = (nominatimResult.get("class"), nominatimResult.get("type"))
    if pair in EDU_TAG_PAIRS:
        return True
    if nominatimResult.get("class") in NOT_CAMPUS:
        return False
    dn = nominatimResult.get("display_name") or ""
    if not isinstance(dn, str):
        dn = str(dn)
    return any(hint in dn.lower() for hint in campusNameHints)


def queryNominatim(q, limit=5):
    p = {
        "q": q,
        "format": "jsonv2",
        "limit": limit,
        "addressdetails": 1,
        "extratags": 1,
        "polygon_geojson": 1,
    }
    throttleNominatim()
    r = requests.get(NOMINATIM_URL, params=p, headers=req_headers, timeout=10)
    r.raise_for_status()
    return r.json()


def fetchOsmLayer(polygon_wkt, layer_key):
    from shapely import wkt as swkt
    poly = swkt.loads(polygon_wkt)
    try:
        gdf = ox.features_from_polygon(poly, tags=campus_tags[layer_key])
        if gdf is None or gdf.empty:
            return None
        gdf = gdf.to_crs("EPSG:4326") if gdf.crs else gdf
        return gdf.__geo_interface__
    except Exception:
        return None
fetchOsmLayer = st.cache_data(show_spinner=False, ttl="6h")(fetchOsmLayer)


def fetchOsmLayerRaw(polygon_wkt, layer_key):
    # Returns raw GeoDataFrame so we can manipulate OSM IDs before JSON conversion
    from shapely import wkt as swkt
    poly = swkt.loads(polygon_wkt)
    try:
        gdf = ox.features_from_polygon(poly, tags=campus_tags[layer_key])
        if gdf is None or gdf.empty:
            return None
        return gdf.to_crs("EPSG:4326") if gdf.crs else gdf
    except Exception:
        return None
fetchOsmLayerRaw = st.cache_data(show_spinner=False, ttl="6h")(fetchOsmLayerRaw)
