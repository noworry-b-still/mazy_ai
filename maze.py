# maze.py
import random
from collections import deque
from stats import AlgorithmStats, calculate_path_length


class MazeCell:
    def __init__(self):
        self.left = {"neighborIndex": -1, "connection": False}
        self.right = {"neighborIndex": -1, "connection": False}
        self.top = {"neighborIndex": -1, "connection": False}
        self.bottom = {"neighborIndex": -1, "connection": False}


def generate_cells(rows, cols):
    maze_size = rows * cols
    cell_map = [MazeCell() for _ in range(maze_size)]
    for i in range(maze_size):
        if i % cols != 0:
            cell_map[i].left = {"neighborIndex": i - 1, "connection": False}
        if (i + 1) % cols != 0:
            cell_map[i].right = {"neighborIndex": i + 1, "connection": False}
        if i - cols >= 0:
            cell_map[i].top = {"neighborIndex": i - cols, "connection": False}
        if i + cols < maze_size:
            cell_map[i].bottom = {"neighborIndex": i + cols, "connection": False}
    return cell_map


def find_all_paths(cell_map, rows, cols):
    paths = []
    maze_size = rows * cols
    for i in range(maze_size):
        right_idx = cell_map[i].right["neighborIndex"]
        if right_idx != -1:
            paths.append(
                {"cell1": i, "cell2": right_idx, "weight": random.randint(0, 99)}
            )
        bottom_idx = cell_map[i].bottom["neighborIndex"]
        if bottom_idx != -1:
            paths.append(
                {"cell1": i, "cell2": bottom_idx, "weight": random.randint(0, 99)}
            )
    return sorted(paths, key=lambda x: x["weight"])


def build_path(cell_map, cell1, cell2, cols):
    if cell2 - cell1 == 1:
        cell_map[cell1].right["connection"] = True
        cell_map[cell2].left["connection"] = True
    elif cell2 - cell1 == cols:
        cell_map[cell1].bottom["connection"] = True
        cell_map[cell2].top["connection"] = True


def select_paths(cell_map, rows, cols):
    paths = find_all_paths(cell_map, rows, cols)
    reps = list(range(rows * cols))

    def find_rep(x):
        return reps[x]

    def set_rep(old, new):
        for i in range(len(reps)):
            if reps[i] == old:
                reps[i] = new

    while True:
        if all(reps[i] == reps[0] for i in range(len(reps))):
            break
        if not paths:
            break
        path = paths.pop(0)
        if find_rep(path["cell1"]) != find_rep(path["cell2"]):
            build_path(cell_map, path["cell1"], path["cell2"], cols)
            old_rep = find_rep(path["cell1"])
            new_rep = find_rep(path["cell2"])
            set_rep(old_rep, new_rep)


def backtrack(search_map, paths_searched, index):
    if index != 0:
        for path in reversed(paths_searched):
            if path["to"] == index:
                search_map[path["from"]]["inSolution"] = True
                backtrack(search_map, paths_searched, path["from"])
                break


def depth_first_search(cell_map, search_map, paths_searched, collect_stats=False):
    """Depth-First Search implementation that returns stats when collect_stats=True"""
    if collect_stats:
        stats = AlgorithmStats("Depth-First Search")
        stats.start_timer()

    stack = [{"cell": 0, "neighbors": cell_map[0]}]
    search_map[0]["searched"] = True
    cells_explored = 0
    max_frontier_size = 0

    while stack:
        max_frontier_size = max(max_frontier_size, len(stack))
        current = stack.pop()
        cell_idx = current["cell"]
        cells_explored += 1

        if cell_idx == len(cell_map) - 1:
            search_map[cell_idx]["inSolution"] = True
            backtrack(search_map, paths_searched, cell_idx)

            if collect_stats:
                stats.cells_explored = cells_explored
                stats.max_frontier_size = max_frontier_size
                stats.path_length = calculate_path_length(paths_searched)
                stats.stop_timer()
                return stats

            return True

        neighbors = current["neighbors"]
        for direction in ["right", "bottom", "left", "top"]:
            n_idx = getattr(neighbors, direction)["neighborIndex"]
            if (
                n_idx != -1
                and getattr(neighbors, direction)["connection"]
                and not search_map[n_idx]["searched"]
            ):
                stack.append({"cell": n_idx, "neighbors": cell_map[n_idx]})
                paths_searched.append({"from": cell_idx, "to": n_idx})
                search_map[n_idx]["searched"] = True
                if not collect_stats:
                    yield

    if collect_stats:
        stats.cells_explored = cells_explored
        stats.max_frontier_size = max_frontier_size
        stats.path_length = 0  # No path found
        stats.stop_timer()
        return stats

    return False


def breadth_first_search(cell_map, search_map, paths_searched, collect_stats=False):
    """Breadth-First Search implementation that returns stats when collect_stats=True"""
    if collect_stats:
        stats = AlgorithmStats("Breadth-First Search")
        stats.start_timer()

    queue = deque([{"cell": 0, "neighbors": cell_map[0]}])
    search_map[0]["searched"] = True
    cells_explored = 0
    max_frontier_size = 0

    while queue:
        max_frontier_size = max(max_frontier_size, len(queue))
        current = queue.popleft()
        cell_idx = current["cell"]
        cells_explored += 1

        if cell_idx == len(cell_map) - 1:
            search_map[cell_idx]["inSolution"] = True
            backtrack(search_map, paths_searched, cell_idx)

            if collect_stats:
                stats.cells_explored = cells_explored
                stats.max_frontier_size = max_frontier_size
                stats.path_length = calculate_path_length(paths_searched)
                stats.stop_timer()
                return stats

            return True

        neighbors = current["neighbors"]
        for direction in ["left", "right", "top", "bottom"]:
            n_idx = getattr(neighbors, direction)["neighborIndex"]
            if (
                n_idx != -1
                and getattr(neighbors, direction)["connection"]
                and not search_map[n_idx]["searched"]
            ):
                queue.append({"cell": n_idx, "neighbors": cell_map[n_idx]})
                paths_searched.append({"from": cell_idx, "to": n_idx})
                search_map[n_idx]["searched"] = True
                if not collect_stats:
                    yield

    if collect_stats:
        stats.cells_explored = cells_explored
        stats.max_frontier_size = max_frontier_size
        stats.path_length = 0  # No path found
        stats.stop_timer()
        return stats

    return False


def a_star_search(
    cell_map, search_map, paths_searched, rows, cols, choice, collect_stats=False
):
    """A* Search implementation that returns stats when collect_stats=True"""
    if collect_stats:
        stats = AlgorithmStats(f"A* Search ({'f = g + h' if choice == 1 else 'f = h'})")
        stats.start_timer()

    manhattan_map = []
    for r in range(rows):
        for c in range(cols):
            cost_to_exit = (rows - 1 - r) + (cols - 1 - c)
            manhattan_map.append({"costToArrive": -1, "costToExit": cost_to_exit})
    manhattan_map[0]["costToArrive"] = 0
    search_map[0]["searched"] = True
    open_list = [{"cell": 0, "neighbors": cell_map[0]}]
    cells_explored = 0
    max_frontier_size = 0

    while open_list:
        max_frontier_size = max(max_frontier_size, len(open_list))

        smallest_cost = float("inf")
        smallest_i = 0
        for i, item in enumerate(open_list):
            idx = item["cell"]
            if choice == 1:
                cost = (
                    manhattan_map[idx]["costToArrive"]
                    + manhattan_map[idx]["costToExit"]
                )
            else:
                cost = manhattan_map[idx]["costToExit"]
            if cost < smallest_cost:
                smallest_cost = cost
                smallest_i = i

        current = open_list.pop(smallest_i)
        cell_idx = current["cell"]
        cells_explored += 1

        if cell_idx == len(cell_map) - 1:
            search_map[cell_idx]["inSolution"] = True
            backtrack(search_map, paths_searched, cell_idx)

            if collect_stats:
                stats.cells_explored = cells_explored
                stats.max_frontier_size = max_frontier_size
                stats.path_length = calculate_path_length(paths_searched)
                stats.stop_timer()
                return stats

            return True

        neighbors = current["neighbors"]
        for direction in ["left", "right", "top", "bottom"]:
            n_idx = getattr(neighbors, direction)["neighborIndex"]
            if n_idx != -1 and getattr(neighbors, direction)["connection"]:
                current_cost = manhattan_map[cell_idx]["costToArrive"]
                neighbor_cost = manhattan_map[n_idx]["costToArrive"]
                if neighbor_cost == -1 or neighbor_cost > current_cost + 1:
                    manhattan_map[n_idx]["costToArrive"] = current_cost + 1
                    if not search_map[n_idx]["searched"]:
                        open_list.append({"cell": n_idx, "neighbors": cell_map[n_idx]})
                        paths_searched.append({"from": cell_idx, "to": n_idx})
                        search_map[n_idx]["searched"] = True
                        if not collect_stats:
                            yield

    if collect_stats:
        stats.cells_explored = cells_explored
        stats.max_frontier_size = max_frontier_size
        stats.path_length = 0  # No path found
        stats.stop_timer()
        return stats

    return False


def uniform_cost_search(cell_map, search_map, paths_searched, collect_stats=False):
    """Uniform Cost Search implementation that returns stats when collect_stats=True"""
    import heapq

    if collect_stats:
        stats = AlgorithmStats("Uniform-Cost Search")
        stats.start_timer()

    pq = [(0, 0, {"cell": 0, "neighbors": cell_map[0]})]
    search_map[0]["searched"] = True
    cost_so_far = {0: 0}
    cells_explored = 0
    max_frontier_size = 0

    while pq:
        max_frontier_size = max(max_frontier_size, len(pq))
        current_cost, _, current = heapq.heappop(pq)
        cell_idx = current["cell"]
        cells_explored += 1

        if cell_idx == len(cell_map) - 1:
            search_map[cell_idx]["inSolution"] = True
            backtrack(search_map, paths_searched, cell_idx)

            if collect_stats:
                stats.cells_explored = cells_explored
                stats.max_frontier_size = max_frontier_size
                stats.path_length = calculate_path_length(paths_searched)
                stats.stop_timer()
                return stats

            return True

        neighbors = current["neighbors"]
        for direction in ["left", "right", "top", "bottom"]:
            n_idx = getattr(neighbors, direction)["neighborIndex"]
            if n_idx != -1 and getattr(neighbors, direction)["connection"]:
                new_cost = current_cost + 1
                if n_idx not in cost_so_far or new_cost < cost_so_far[n_idx]:
                    cost_so_far[n_idx] = new_cost
                    heapq.heappush(
                        pq,
                        (
                            new_cost,
                            n_idx,
                            {"cell": n_idx, "neighbors": cell_map[n_idx]},
                        ),
                    )
                    if not search_map[n_idx]["searched"]:
                        paths_searched.append({"from": cell_idx, "to": n_idx})
                        search_map[n_idx]["searched"] = True
                        if not collect_stats:
                            yield

    if collect_stats:
        stats.cells_explored = cells_explored
        stats.max_frontier_size = max_frontier_size
        stats.path_length = 0  # No path found
        stats.stop_timer()
        return stats

    return False


def ant_colony_optimization(
    cell_map, search_map, paths_searched, rows, cols, collect_stats=False
):
    """Ant Colony Optimization implementation that returns stats when collect_stats=True"""
    if collect_stats:
        stats = AlgorithmStats("Ant Colony Optimization")
        stats.start_timer()

    num_ants = 10
    num_iterations = 5
    alpha = 1.0
    beta = 2.0
    evaporation_rate = 0.5

    pheromone = {}
    for i in range(len(cell_map)):
        neighbors = cell_map[i]
        for direction in ["left", "right", "top", "bottom"]:
            n_idx = getattr(neighbors, direction)["neighborIndex"]
            if n_idx != -1 and getattr(neighbors, direction)["connection"]:
                pheromone[(i, n_idx)] = 0.1

    best_path = None
    best_path_length = float("inf")
    cells_explored = 0
    max_frontier_size = 0

    exit_idx = rows * cols - 1
    exit_row = exit_idx // cols
    exit_col = exit_idx % cols

    def get_heuristic(idx):
        row = idx // cols
        col = idx % cols
        return abs(row - exit_row) + abs(col - exit_col)

    for iteration in range(num_iterations):
        all_paths = []
        all_path_lengths = []

        for ant in range(num_ants):
            current_node = 0
            path = [current_node]
            visited = {0: True}
            ant_cells_explored = 0

            while current_node != exit_idx:
                ant_cells_explored += 1
                neighbors = cell_map[current_node]
                possible_moves = []

                for direction in ["left", "right", "top", "bottom"]:
                    n_idx = getattr(neighbors, direction)["neighborIndex"]
                    if (
                        n_idx != -1
                        and getattr(neighbors, direction)["connection"]
                        and n_idx not in visited
                    ):
                        possible_moves.append(n_idx)

                if not possible_moves:
                    if len(path) > 1:
                        path.pop()
                        current_node = path[-1]
                        continue
                    else:
                        break

                probabilities = []
                for next_node in possible_moves:
                    tau = pheromone.get((current_node, next_node), 0.1)
                    eta = 1.0 / (get_heuristic(next_node) + 1)
                    prob = (tau**alpha) * (eta**beta)
                    probabilities.append(prob)

                total = sum(probabilities)
                if total == 0:
                    probabilities = [1.0 / len(possible_moves)] * len(possible_moves)
                else:
                    probabilities = [p / total for p in probabilities]

                r = random.random()
                cumulative_prob = 0
                chosen_idx = 0

                for i, prob in enumerate(probabilities):
                    cumulative_prob += prob
                    if r <= cumulative_prob:
                        chosen_idx = i
                        break

                next_node = possible_moves[chosen_idx]
                path.append(next_node)
                visited[next_node] = True
                current_node = next_node

                if not search_map[next_node]["searched"]:
                    search_map[next_node]["searched"] = True
                    paths_searched.append({"from": path[-2], "to": next_node})
                    if not collect_stats:
                        yield

            cells_explored += ant_cells_explored
            max_frontier_size = max(max_frontier_size, len(visited))

            if current_node == exit_idx:
                path_length = len(path) - 1
                all_paths.append(path)
                all_path_lengths.append(path_length)

                if path_length < best_path_length:
                    best_path = path
                    best_path_length = path_length

        for edge in pheromone:
            pheromone[edge] *= 1 - evaporation_rate

        for i, path in enumerate(all_paths):
            path_length = all_path_lengths[i]
            deposit = 1.0 / path_length if path_length > 0 else 0
            for j in range(len(path) - 1):
                edge = (path[j], path[j + 1])
                pheromone[edge] = pheromone.get(edge, 0) + deposit

    if best_path:
        for i in range(len(best_path)):
            node = best_path[i]
            search_map[node]["inSolution"] = True

        if collect_stats:
            stats.cells_explored = cells_explored
            stats.max_frontier_size = max_frontier_size
            stats.path_length = best_path_length
            stats.stop_timer()
            return stats

        return True

    if collect_stats:
        stats.cells_explored = cells_explored
        stats.max_frontier_size = max_frontier_size
        stats.path_length = 0  # No path found
        stats.stop_timer()
        return stats

    return False
