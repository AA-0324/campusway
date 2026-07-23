# CampusWay
CampusWay is an interactive geospatial web application designed to help new university students, freshmen, and visitors navigate sprawling college campuses. The app dynamically queries spatial vector data from OpenStreetMap to render color-coded campus layouts, building footprints, pedestrian pathways, and specialized facilities.

---

## Motivation and Problem Statement

Navigating a new university campus during orientation and the first weeks of classes is a major source of stress for incoming freshmen. Sprawling campuses often span hundreds of acres with dozens of interconnected buildings and pedestrian paths. 

Existing navigation tools present key limitations:
1. Standard vehicular navigation apps (e.g., Google Maps, Apple Maps) prioritize roads and driving routes, frequently missing pedestrian-only pathways, inner courtyards, and specific building outlines.
2. University PDF orientation maps are static, non-interactive, difficult to search on mobile devices, and quickly become outdated.

I built CampusWay to solve this problem. By combining real-time spatial geocoding with vector feature extraction, CampusWay allows students to search for any university globally and view an interactive, layer-controlled map that highlights exactly where they need to walk.

---

## Technical Features

- Natural Language Campus Search: Resolves global university, college, and institute names into spatial boundary polygons via Nominatim API integrations.
- Layer-Based Spatial Isolation: Allows users to independently toggle visual layers for campus buildings, primary pedestrian pathways, roads, and specialized facilities (libraries, dining halls, fitness centers).
- Interactive Leafmap Dashboard: Supports dynamic panning, zooming, full-screen viewing, and custom spatial color encoding.
- API Rate Limiting and Caching: Implements session-state time gaps and resource caching to maintain responsiveness while complying with external API usage policies.

---

## Engineering Challenges and Solutions

Building CampusWay required resolving several data engineering and geospatial processing hurdles:

1. Handling Unstructured Geocoding Boundaries
Search queries for universities can return city points, whole administrative districts, or point locations instead of physical campus boundaries. I constructed a verification function that checks spatial tags, filters out non-educational amenities, and dynamically falls back to boundary geocoding if initial polygon data is missing.

2. Polygon Duplication and Layer Overlap
OpenStreetMap often tags specialized structures (such as campus libraries or sports complexes) under both general building tags and specialized amenity tags. Rendering both layers directly caused overlapping polygon artifacts and visual clutter. To resolve this, I engineered a deduplication function that extracts underlying OpenStreetMap IDs from GeoPandas MultiIndex structures, stripping duplicate building geometries before the final map compile.

3. Efficient Geospatial Caching in Streamlit
Streamlit re-runs scripts on user interactions, which can lead to repetitive spatial API calls and app crashes due to non-serializable GeoDataFrame caching. I solved this by serializing geometries into WKT (Well-Known Text) strings for caching, preserving performance while keeping API calls to a minimum.

---

## Technology Stack

- Language: Python 3.10+
- Web Framework: Streamlit
- Spatial Data Extraction: OSMnx, Shapely, GeoPandas, Requests
- Map Rendering: Leafmap, Folium
- Data Source: OpenStreetMap / Nominatim API

---

## License

Distributed under the MIT License. See LICENSE file for full terms.


:)
