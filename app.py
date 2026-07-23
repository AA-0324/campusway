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
