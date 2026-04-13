from __future__ import annotations

import heapq
import math
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple

from airport import Airport


@dataclass
class PathResult:
    distances: Dict[str, float]
    previous: Dict[str, Optional[str]]


class AirportGraph:
    """Grafo simple, no dirigido y ponderado (lista de adyacencia)."""

    def __init__(self) -> None:
        self.vertices: Dict[str, Airport] = {}
        self.adj: Dict[str, Dict[str, float]] = defaultdict(dict)

    def add_airport(self, airport: Airport) -> None:
        self.vertices[airport.code] = airport
        self.adj.setdefault(airport.code, {})

    def add_edge(self, u: str, v: str, weight: float) -> None:
        if u == v:
            return
        if u not in self.vertices or v not in self.vertices:
            raise ValueError("Ambos aeropuertos deben existir antes de crear una ruta")
        current = self.adj[u].get(v)
        if current is None or weight < current:
            self.adj[u][v] = weight
            self.adj[v][u] = weight

    def connected_components(self) -> List[Set[str]]:
        visited: Set[str] = set()
        components: List[Set[str]] = []

        for start in self.vertices:
            if start in visited:
                continue
            queue = deque([start])
            visited.add(start)
            comp = {start}
            while queue:
                node = queue.popleft()
                for neigh in self.adj[node]:
                    if neigh not in visited:
                        visited.add(neigh)
                        comp.add(neigh)
                        queue.append(neigh)
            components.append(comp)
        return components

    def connectivity_report(self) -> dict:
        comps = self.connected_components()
        return {
            "is_connected": len(comps) == 1,
            "num_components": len(comps),
            "component_sizes": sorted([len(c) for c in comps], reverse=True),
        }

    def is_bipartite_component(self, nodes: Iterable[str]) -> bool:
        nodes_set = set(nodes)
        color: Dict[str, int] = {}

        for start in nodes_set:
            if start in color:
                continue
            queue = deque([start])
            color[start] = 0
            while queue:
                node = queue.popleft()
                for neigh in self.adj[node]:
                    if neigh not in nodes_set:
                        continue
                    if neigh not in color:
                        color[neigh] = 1 - color[node]
                        queue.append(neigh)
                    elif color[neigh] == color[node]:
                        return False
        return True

    def bipartite_report_largest_component(self) -> dict:
        comps = self.connected_components()
        if not comps:
            return {"checked_component_size": 0, "is_bipartite": True}
        largest = max(comps, key=len)
        return {
            "checked_component_size": len(largest),
            "is_bipartite": self.is_bipartite_component(largest),
        }

    def _edges_of_component(self, nodes: Set[str]) -> List[Tuple[float, str, str]]:
        edges: List[Tuple[float, str, str]] = []
        seen: Set[Tuple[str, str]] = set()
        for u in nodes:
            for v, w in self.adj[u].items():
                key = tuple(sorted((u, v)))
                if v in nodes and key not in seen:
                    seen.add(key)
                    edges.append((w, u, v))
        edges.sort(key=lambda x: x[0])
        return edges

    def mst_weight_per_component(self) -> List[dict]:
        """Kruskal por componente conexa."""

        def kruskal(nodes: Set[str]) -> float:
            parent = {n: n for n in nodes}
            rank = {n: 0 for n in nodes}

            def find(x: str) -> str:
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x

            def union(a: str, b: str) -> bool:
                ra, rb = find(a), find(b)
                if ra == rb:
                    return False
                if rank[ra] < rank[rb]:
                    parent[ra] = rb
                elif rank[ra] > rank[rb]:
                    parent[rb] = ra
                else:
                    parent[rb] = ra
                    rank[ra] += 1
                return True

            total = 0.0
            for w, u, v in self._edges_of_component(nodes):
                if union(u, v):
                    total += w
            return total

        output = []
        for i, comp in enumerate(self.connected_components(), start=1):
            output.append(
                {
                    "component_id": i,
                    "num_vertices": len(comp),
                    "mst_weight_km": kruskal(comp),
                }
            )
        return output

    def dijkstra(self, source: str) -> PathResult:
        if source not in self.vertices:
            raise ValueError(f"No existe el aeropuerto: {source}")

        dist = {node: math.inf for node in self.vertices}
        prev: Dict[str, Optional[str]] = {node: None for node in self.vertices}
        dist[source] = 0.0
        heap: List[Tuple[float, str]] = [(0.0, source)]

        while heap:
            current_dist, node = heapq.heappop(heap)
            if current_dist > dist[node]:
                continue
            for neigh, weight in self.adj[node].items():
                cand = current_dist + weight
                if cand < dist[neigh]:
                    dist[neigh] = cand
                    prev[neigh] = node
                    heapq.heappush(heap, (cand, neigh))

        return PathResult(distances=dist, previous=prev)

    def shortest_path(self, source: str, target: str) -> Tuple[float, List[str]]:
        result = self.dijkstra(source)
        if target not in self.vertices:
            raise ValueError(f"No existe el aeropuerto: {target}")
        if result.distances[target] == math.inf:
            return math.inf, []

        path: List[str] = []
        cur: Optional[str] = target
        while cur is not None:
            path.append(cur)
            cur = result.previous[cur]
        path.reverse()
        return result.distances[target], path

    def top_10_longest_shortest_paths(self, source: str) -> List[Tuple[str, float]]:
        result = self.dijkstra(source)
        reachable = [(code, d) for code, d in result.distances.items() if d < math.inf and code != source]
        reachable.sort(key=lambda x: x[1], reverse=True)
        return reachable[:10]
