# 🧭 CampusWay

An interactive geospatial web app built with Python and Streamlit that renders university campuses, pedestrian pathways, building footprints, and facilities using live OpenStreetMap (OSM) vector data.


## Why I Built This

When freshmen arrive on a college campus for their first week of classes, finding specific buildings or walking routes is extremely frustrating. Navigation apps like Google Maps or Apple Maps are designed with driving in mind. They prioritize roads and often show campus grounds as just a blank gray or green patch, completely skipping footpaths, courtyards, and distinct buildings. On the other hand, official university/college maps are usually PDFs that are impossible to read on a phone and can't be searched interactively. I built CampusWay to solve this. You type in any university or college name, and the app builds a custom interactive map showing where students actually walk and where students can find specific buildings and facilities.


## Inspiration
When freshmen arrive on a college campus, navigating complex layouts and finding specific buildings is often overwhelming. Commercial navigation tools like Google Maps are built for driving—they frequently drop pins at parking lots or perimeter gates while rendering campus grounds as plain green or gray patches. Official university maps are usually static PDFs that are clunky to read on mobile devices and cannot be searched interactively. CampusWay solves this by querying live vector data to build interactive, pedestrian-focused maps on demand for any university worldwide.


## Features
* OSM Data: Queries and renders buildings, pedestrian pathways, service routes, and specialized facilities (libraries, dining halls, sports centers).
* Typo-Resistant Search: Powered by a custom Levenshtein edit distance algorithm, allowing users to locate buildings even if they misspell names while walking.
* Interactive Ruler: Measures real walking distances between points.
* Proximity Detection: Calculates nearby facilities and buildings relative to any selected location using the Haversine formula.
* Layer Control: Allows users to toggle individual spatial layers (Buildings, Paths, Roads, Facilities) to customize map views.


## Stack
* Framework/UI: Python, Streamlit, Folium, Leafmap
* Geospatial: GeoPandas, OSMnx, Shapely
* APIs/Data: Overpass API, Nominatim, Photon


## Technical Feats
* Deadlines: External network queries to Overpass mirrors are handled asynchronously using `concurrent.futures.ThreadPoolExecutor` governed by a custom timeout wrapper. Unresponsive endpoints are abandoned to keep it working.
* Levenshtein Algorithm: Implemented a zero-dependency Levenshtein distance algorithm from scratch to calculate insertion, deletion, and substitution costs for string matching.
* Optimization: Geometry simplification (`shapely.geometry.simplify`) and area-based feature capping ensure fast web rendering.
