from src.graph.airport_graph import Airport, AirportGraph


def test_shortest_path_and_components():
    g = AirportGraph()
    g.add_airport(Airport("A", "A", "X", "CO", 0, 0))
    g.add_airport(Airport("B", "B", "X", "CO", 0, 1))
    g.add_airport(Airport("C", "C", "X", "CO", 0, 2))

    g.add_route("A", "B", 2)
    g.add_route("B", "C", 2)
    g.add_route("A", "C", 10)

    dist, path = g.shortest_path("A", "C")
    assert dist == 4
    assert path == ["A", "B", "C"]
    assert len(g.connected_components()) == 1
    assert g.is_bipartite() is False
