from __future__ import annotations

from typing import Dict, List

from src.graph.airport_graph import AirportGraph


def analyze_graph(graph: AirportGraph, source: str | None = None, target: str | None = None) -> Dict:
    components = graph.connected_components()
    largest_component = max(components, key=len) if components else set()
    source = source or (next(iter(graph.vertices)) if graph.vertices else None)

    longest_paths: List[Dict] = []
    if source:
        distances = graph.shortest_paths_from(source)
        finite = [(node, dist) for node, dist in distances.items() if dist != float("inf")]
        finite.sort(key=lambda x: x[1], reverse=True)
        longest_paths = [{"target": n, "distance_km": round(d, 2)} for n, d in finite[:10]]

    shortest = None
    if source and target and source in graph.vertices and target in graph.vertices:
        dist, path = graph.shortest_path(source, target)
        shortest = {
            "source": source,
            "target": target,
            "distance_km": round(dist, 2) if path else None,
            "path": path,
        }

    return {
        "num_components": len(components),
        "component_sizes": sorted([len(c) for c in components], reverse=True),
        "is_bipartite_global": graph.is_bipartite(),
        "is_bipartite_largest_component": graph.is_bipartite(largest_component) if largest_component else True,
        "mst_weight_by_component_km": [round(w, 2) for w in graph.minimum_spanning_tree_weight(by_component=True)],
        "source": source,
        "top_10_longest_shortest_paths": longest_paths,
        "shortest_path_query": shortest,
    }
