from __future__ import annotations

from pathlib import Path
from typing import List

from graph import AirportGraph


def _ensure_folium():
    try:
        import folium
    except ImportError as exc:
        raise RuntimeError("Instala folium para generar mapas: pip install folium") from exc
    return folium


def create_airports_map(graph: AirportGraph, output_html: str = "map_aeropuertos.html") -> str:
    folium = _ensure_folium()
    if not graph.vertices:
        raise ValueError("El grafo no tiene aeropuertos")

    first = next(iter(graph.vertices.values()))
    m = folium.Map(location=[first.lat, first.lon], zoom_start=3)

    for airport in graph.vertices.values():
        folium.CircleMarker(
            location=[airport.lat, airport.lon],
            radius=3,
            popup=f"{airport.code} - {airport.name} ({airport.city}, {airport.country})",
            color="#1f77b4",
            fill=True,
        ).add_to(m)

    m.save(output_html)
    return str(Path(output_html).resolve())


def create_path_map(graph: AirportGraph, path: List[str], output_html: str = "map_camino_minimo.html") -> str:
    folium = _ensure_folium()
    if not path:
        raise ValueError("No se puede dibujar un camino vacío")

    coords = [(graph.vertices[c].lat, graph.vertices[c].lon) for c in path]
    m = folium.Map(location=coords[0], zoom_start=4)

    for i, code in enumerate(path):
        airport = graph.vertices[code]
        icon_color = "green" if i == 0 else "red" if i == len(path) - 1 else "blue"
        folium.Marker(
            location=[airport.lat, airport.lon],
            popup=(
                f"{airport.code} - {airport.name}<br>"
                f"{airport.city}, {airport.country}<br>"
                f"Lat: {airport.lat:.4f} Lon: {airport.lon:.4f}"
            ),
            icon=folium.Icon(color=icon_color),
        ).add_to(m)

    folium.PolyLine(coords, weight=3, color="purple").add_to(m)
    m.save(output_html)
    return str(Path(output_html).resolve())
