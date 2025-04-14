# stats.py
import time


class AlgorithmStats:
    def __init__(self, algorithm_name):
        self.algorithm_name = algorithm_name
        self.cells_explored = 0
        self.max_frontier_size = 0
        self.path_length = 0
        self.execution_time = 0
        self.start_time = 0

    def start_timer(self):
        self.start_time = time.time()

    def stop_timer(self):
        self.execution_time = time.time() - self.start_time

    def __str__(self):
        return (
            f"{self.algorithm_name}:\n"
            f"  Cells explored: {self.cells_explored}\n"
            f"  Max frontier size: {self.max_frontier_size}\n"
            f"  Solution path length: {self.path_length}\n"
            f"  Execution time: {self.execution_time:.4f} seconds"
        )


def calculate_path_length(paths_searched):
    """Calculate the length of the solution path"""
    # Create a graph of connections
    graph = {}
    for path in paths_searched:
        from_node = path["from"]
        to_node = path["to"]
        if from_node not in graph:
            graph[from_node] = []
        graph[from_node].append(to_node)

    # Find path from start (0) to end (last node)
    from collections import deque

    # Find the end node (highest node in paths_searched)
    end_node = max([path["to"] for path in paths_searched] + [0])

    # Use BFS to find shortest path in the discovered graph
    queue = deque([(0, [0])])  # (node, path so far)
    visited = {0}

    while queue:
        node, path = queue.popleft()
        if node == end_node:
            return len(path) - 1  # Number of steps (edges)

        if node in graph:
            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

    return 0  # No path found
