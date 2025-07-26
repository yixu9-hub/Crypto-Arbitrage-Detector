# Bellman-Ford core logic without consideration of gas handling

def bellman_ford(graph, start):
    # Initialize distances from start to all vertices as infinite
    distances = {vertex: float('inf') for vertex in graph}
    distances[start] = 0  # Distance from start to itself is 0

    # Relax edges up to |V| - 1 times
    for _ in range(len(graph) - 1):
        for vertex in graph:
            for neighbor, weight in graph[vertex].items():
                if distances[vertex] + weight < distances[neighbor]:
                    distances[neighbor] = distances[vertex] + weight

    # Check for negative-weight cycles
    for vertex in graph:
        for neighbor, weight in graph[vertex].items():
            if distances[vertex] + weight < distances[neighbor]:
                raise ValueError("Graph contains a negative-weight cycle")

    return distances