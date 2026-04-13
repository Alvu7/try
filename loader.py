from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Tuple

from airport import Airport
from graph import AirportGraph
from utils import haversine_km, normalize_code

REQUIRED_COLUMNS = {
    "origin_code": ["origin_code", "origen_codigo", "source_code", "iata_origen"],
    "origin_name": ["origin_name", "origen_nombre", "source_name"],
    "origin_city": ["origin_city", "origen_ciudad", "source_city"],
    "origin_country": ["origin_country", "origen_pais", "source_country"],
    "origin_lat": ["origin_lat", "origen_lat", "source_lat", "lat_origen"],
    "origin_lon": ["origin_lon", "origen_lon", "source_lon", "lon_origen"],
    "destination_code": ["destination_code", "destino_codigo", "target_code", "iata_destino"],
    "destination_name": ["destination_name", "destino_nombre", "target_name"],
    "destination_city": ["destination_city", "destino_ciudad", "target_city"],
    "destination_country": ["destination_country", "destino_pais", "target_country"],
    "destination_lat": ["destination_lat", "destino_lat", "target_lat", "lat_destino"],
    "destination_lon": ["destination_lon", "destino_lon", "target_lon", "lon_destino"],
}


def _normalize_headers(headers: List[str]) -> Dict[str, int]:
    lower = {h.strip().lower(): i for i, h in enumerate(headers)}
    out: Dict[str, int] = {}
    for canonical, aliases in REQUIRED_COLUMNS.items():
        idx = next((lower[a] for a in aliases if a in lower), None)
        if idx is None:
            raise ValueError(f"Falta columna requerida: {canonical}")
        out[canonical] = idx
    return out


def load_graph_from_csv(file_path: str) -> Tuple[AirportGraph, dict]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {file_path}")

    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))

    if not rows:
        raise ValueError("Archivo vacío")

    header_map = _normalize_headers(rows[0])
    graph = AirportGraph()

    seen_routes = set()
    stats = {
        "rows_total": max(0, len(rows) - 1),
        "rows_invalid": 0,
        "duplicates_skipped": 0,
    }

    for row in rows[1:]:
        try:
            origin_code = normalize_code(row[header_map["origin_code"]])
            destination_code = normalize_code(row[header_map["destination_code"]])
            if not origin_code or not destination_code:
                stats["rows_invalid"] += 1
                continue

            o_lat = float(row[header_map["origin_lat"]])
            o_lon = float(row[header_map["origin_lon"]])
            d_lat = float(row[header_map["destination_lat"]])
            d_lon = float(row[header_map["destination_lon"]])

            if origin_code not in graph.vertices:
                graph.add_airport(
                    Airport(
                        code=origin_code,
                        name=row[header_map["origin_name"]].strip(),
                        city=row[header_map["origin_city"]].strip(),
                        country=row[header_map["origin_country"]].strip(),
                        lat=o_lat,
                        lon=o_lon,
                    )
                )
            if destination_code not in graph.vertices:
                graph.add_airport(
                    Airport(
                        code=destination_code,
                        name=row[header_map["destination_name"]].strip(),
                        city=row[header_map["destination_city"]].strip(),
                        country=row[header_map["destination_country"]].strip(),
                        lat=d_lat,
                        lon=d_lon,
                    )
                )

            key = tuple(sorted((origin_code, destination_code)))
            if key in seen_routes:
                stats["duplicates_skipped"] += 1
                continue
            seen_routes.add(key)

            dist = haversine_km(o_lat, o_lon, d_lat, d_lon)
            graph.add_edge(origin_code, destination_code, dist)
        except (IndexError, ValueError):
            stats["rows_invalid"] += 1

    stats["airports"] = len(graph.vertices)
    stats["routes"] = sum(len(v) for v in graph.adj.values()) // 2
    return graph, stats
