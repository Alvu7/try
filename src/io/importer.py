from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Tuple

from src.graph.airport_graph import Airport, AirportGraph

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
    normalized = {h.strip().lower(): i for i, h in enumerate(headers)}
    resolved: Dict[str, int] = {}
    for canonical, aliases in REQUIRED_COLUMNS.items():
        idx = next((normalized[a] for a in aliases if a in normalized), None)
        if idx is None:
            raise ValueError(f"Falta columna requerida: {canonical}")
        resolved[canonical] = idx
    return resolved


def _read_rows(path: Path) -> List[List[str]]:
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8", newline="") as f:
            return list(csv.reader(f))

    if path.suffix.lower() in {".xlsx", ".xls"}:
        try:
            import openpyxl
        except ImportError as exc:
            raise ValueError("Para Excel instala openpyxl: pip install openpyxl") from exc

        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active
        rows = []
        for row in ws.iter_rows(values_only=True):
            rows.append(["" if value is None else str(value) for value in row])
        return rows

    raise ValueError("Formato no soportado. Usa .csv, .xlsx o .xls")


def load_dataset(file_path: str) -> Tuple[AirportGraph, Dict[str, int]]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {file_path}")

    rows = _read_rows(path)
    if not rows:
        raise ValueError("Archivo vacío")

    header_map = _normalize_headers(rows[0])
    graph = AirportGraph()
    duplicate_count = 0
    invalid_coords = 0
    null_rows = 0
    seen_routes = set()

    for row in rows[1:]:
        if len(row) < len(rows[0]):
            row += [""] * (len(rows[0]) - len(row))

        try:
            origin_code = row[header_map["origin_code"]].strip().upper()
            destination_code = row[header_map["destination_code"]].strip().upper()

            required_values = [row[header_map[k]].strip() for k in REQUIRED_COLUMNS]
            if any(v == "" for v in required_values):
                null_rows += 1
                continue

            o_lat = float(row[header_map["origin_lat"]])
            o_lon = float(row[header_map["origin_lon"]])
            d_lat = float(row[header_map["destination_lat"]])
            d_lon = float(row[header_map["destination_lon"]])

            if not (-90 <= o_lat <= 90 and -90 <= d_lat <= 90 and -180 <= o_lon <= 180 and -180 <= d_lon <= 180):
                invalid_coords += 1
                continue

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

            route_key = tuple(sorted((origin_code, destination_code)))
            if route_key in seen_routes:
                duplicate_count += 1
                continue
            seen_routes.add(route_key)

            distance = AirportGraph.haversine_km(o_lat, o_lon, d_lat, d_lon)
            graph.add_route(origin_code, destination_code, distance)

        except (ValueError, IndexError):
            null_rows += 1

    stats = {
        "airports": len(graph.vertices),
        "routes": sum(len(n) for n in graph.adj.values()) // 2,
        "duplicates_skipped": duplicate_count,
        "invalid_coordinates_skipped": invalid_coords,
        "null_or_invalid_rows_skipped": null_rows,
    }

    return graph, stats
