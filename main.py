from __future__ import annotations

from graph import AirportGraph
from loader import load_graph_from_csv
from map_view import create_airports_map, create_path_map
from utils import normalize_code


def print_airport_info(graph: AirportGraph, code: str) -> None:
    airport = graph.vertices[code]
    print(f"Código: {airport.code}")
    print(f"Nombre: {airport.name}")
    print(f"Ciudad: {airport.city}")
    print(f"País: {airport.country}")
    print(f"Latitud: {airport.lat}")
    print(f"Longitud: {airport.lon}")


def option_connectivity(graph: AirportGraph) -> None:
    report = graph.connectivity_report()
    print(f"¿Grafo conexo?: {report['is_connected']}")
    if not report["is_connected"]:
        print(f"Componentes: {report['num_components']}")
        for i, size in enumerate(report["component_sizes"], start=1):
            print(f"  - Componente {i}: {size} vértices")


def option_bipartite(graph: AirportGraph) -> None:
    report = graph.bipartite_report_largest_component()
    print("Bipartición evaluada sobre la componente más grande")
    print(f"Tamaño componente: {report['checked_component_size']}")
    print(f"¿Es bipartita?: {report['is_bipartite']}")


def option_mst(graph: AirportGraph) -> None:
    mst_by_component = graph.mst_weight_per_component()
    print("Peso MST por componente:")
    for item in mst_by_component:
        print(
            f"  - Componente {item['component_id']} ({item['num_vertices']} vértices): "
            f"{item['mst_weight_km']:.2f} km"
        )


def option_source_queries(graph: AirportGraph) -> None:
    source = normalize_code(input("Código aeropuerto origen: "))
    if source not in graph.vertices:
        print("No existe ese aeropuerto en el grafo.")
        return

    print("\nInformación del aeropuerto origen")
    print_airport_info(graph, source)

    print("\nTop 10 caminos mínimos más largos desde el origen")
    for code, dist in graph.top_10_longest_shortest_paths(source):
        airport = graph.vertices[code]
        print(f"- {code} | {airport.name} | {airport.city}, {airport.country} | {dist:.2f} km")


def option_shortest_path(graph: AirportGraph) -> None:
    source = normalize_code(input("Código aeropuerto origen: "))
    target = normalize_code(input("Código aeropuerto destino: "))

    if source not in graph.vertices or target not in graph.vertices:
        print("Origen o destino no existe en el grafo.")
        return

    dist, path = graph.shortest_path(source, target)
    if not path:
        print("No existe camino entre esos aeropuertos.")
        return

    print(f"Distancia mínima: {dist:.2f} km")
    print("Camino:", " -> ".join(path))
    if len(path) > 2:
        print("\nVértices intermedios:")
        for code in path[1:-1]:
            print_airport_info(graph, code)
            print("-" * 40)

    html = create_path_map(graph, path)
    print(f"Mapa de camino mínimo generado: {html}")


def option_airports_map(graph: AirportGraph) -> None:
    html = create_airports_map(graph)
    print(f"Mapa general de aeropuertos generado: {html}")


def menu(graph: AirportGraph) -> None:
    options = {
        "1": option_connectivity,
        "2": option_bipartite,
        "3": option_mst,
        "4": option_source_queries,
        "5": option_shortest_path,
        "6": option_airports_map,
    }

    while True:
        print("\n=== LABORATORIO GRAFOS - RUTAS AÉREAS ===")
        print("1) Conexidad y componentes")
        print("2) Bipartición (componente más grande)")
        print("3) MST por componente")
        print("4) Consultas desde aeropuerto origen")
        print("5) Camino mínimo entre dos aeropuertos")
        print("6) Generar mapa general de aeropuertos (HTML)")
        print("0) Salir")

        choice = input("Seleccione una opción: ").strip()
        if choice == "0":
            print("Hasta luego.")
            break

        handler = options.get(choice)
        if handler is None:
            print("Opción inválida.")
            continue

        try:
            handler(graph)
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    path = input("Ruta de flights_final.csv: ").strip()
    g, stats = load_graph_from_csv(path)

    print("\nCarga completa")
    print(f"- Filas totales: {stats['rows_total']}")
    print(f"- Aeropuertos: {stats['airports']}")
    print(f"- Rutas (sin duplicados A-B/B-A): {stats['routes']}")
    print(f"- Duplicadas ignoradas: {stats['duplicates_skipped']}")
    print(f"- Filas inválidas: {stats['rows_invalid']}")

    menu(g)
