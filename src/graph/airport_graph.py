from __future__ import annotations

import heapq
import math
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple


@dataclass(frozen=True)
class Airport:
    code: str
    name: str
    city: str
    country: str
    lat: float
    lon: float


class AirportGraph:
    """Grafo no dirigido, simple y ponderado para aeropuertos."""

    def __init__(self) -> None:
        self.vertices: Dict[str, Airport] = {}
        self.adj: Dict[str, Dict[str, float]] = defaultdict(dict)

    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        radius_km = 6371.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return 2 * radius_km * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def add_airport(self, airport: Airport) -> None:
        self.vertices[airport.code] = airport
        self.adj.setdefault(airport.code, {})

    def add_route(self, origin: str, destination: str, weight: float) -> None:
        if origin == destination:
            return
        if origin not in self.vertices or destination not in self.vertices:
            raise ValueError("Los vértices deben existir antes de agregar una ruta")
        current = self.adj[origin].get(destination)
        if current is None or weight < current:
            self.adj[origin][destination] = weight
            self.adj[destination][origin] = weight

    def connected_components(self) -> List[Set[str]]:
        visited: Set[str] = set()
        components: List[Set[str]] = []
        for node in self.vertices:
            if node in visited:
                continue
            queue = deque([node])
            visited.add(node)
            component = {node}
            while queue:
                curr = queue.popleft()
                for neighbor in self.adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        component.add(neighbor)
                        queue.append(neighbor)
            components.append(component)
        return components

    def is_bipartite(self, component: Optional[Iterable[str]] = None) -> bool:
        nodes = set(component) if component is not None else set(self.vertices)
        color: Dict[str, int] = {}
        for node in nodes:
            if node in color:
                continue
            queue = deque([node])
            color[node] = 0
            while queue:
                curr = queue.popleft()
                for neighbor in self.adj[curr]:
                    if neighbor not in nodes:
                        continue
                    if neighbor not in color:
                        color[neighbor] = 1 - color[curr]
                        queue.append(neighbor)
                    elif color[neighbor] == color[curr]:
                        return False
        return True

    def _component_edges(self, nodes: Set[str]) -> List[Tuple[float, str, str]]:
        edges = []
        seen = set()
        for u in nodes:
            for v, w in self.adj[u].items():
                key = tuple(sorted((u, v)))
                if v in nodes and key not in seen:
                    seen.add(key)
                    edges.append((w, u, v))
        return edges

    def minimum_spanning_tree_weight(self, by_component: bool = True):
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
            for w, u, v in sorted(self._component_edges(nodes)):
                if union(u, v):
                    total += w
            return total

        if by_component:
            return [kruskal(component) for component in self.connected_components()]

        all_nodes = set(self.vertices.keys())
        return kruskal(all_nodes)

    def shortest_paths_from(self, source_code: str) -> Dict[str, float]:
        if source_code not in self.vertices:
            raise ValueError(f"No existe el aeropuerto {source_code}")

        distances = {node: math.inf for node in self.vertices}
        distances[source_code] = 0.0
        heap = [(0.0, source_code)]

        while heap:
            current_distance, node = heapq.heappop(heap)
            if current_distance > distances[node]:
                continue
            for neighbor, weight in self.adj[node].items():
                candidate = current_distance + weight
                if candidate < distances[neighbor]:
                    distances[neighbor] = candidate
                    heapq.heappush(heap, (candidate, neighbor))
        return distances

    def shortest_path(self, source_code: str, target_code: str) -> Tuple[float, List[str]]:
        if source_code not in self.vertices or target_code not in self.vertices:
            raise ValueError("Origen o destino no existe")

        distances = {node: math.inf for node in self.vertices}
        previous: Dict[str, Optional[str]] = {node: None for node in self.vertices}
        distances[source_code] = 0.0
        heap = [(0.0, source_code)]

        while heap:
            current_distance, node = heapq.heappop(heap)
            if node == target_code:
                break
            if current_distance > distances[node]:
                continue
            for neighbor, weight in self.adj[node].items():
                candidate = current_distance + weight
                if candidate < distances[neighbor]:
                    distances[neighbor] = candidate
                    previous[neighbor] = node
                    heapq.heappush(heap, (candidate, neighbor))

        if distances[target_code] == math.inf:
            return math.inf, []

        path = []
        cursor: Optional[str] = target_code
        while cursor is not None:
            path.append(cursor)
            cursor = previous[cursor]
        path.reverse()
        return distances[target_code], path
