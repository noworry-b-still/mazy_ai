# maze.py
import random
from collections import deque


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


def depth_first_search(cell_map, search_map, paths_searched):
    stack = [{"cell": 0, "neighbors": cell_map[0]}]
    search_map[0]["searched"] = True
    while stack:
        current = stack.pop()
        cell_idx = current["cell"]
        if cell_idx == len(cell_map) - 1:
            search_map[cell_idx]["inSolution"] = True
            backtrack(search_map, paths_searched, cell_idx)
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
                yield
    return False


def breadth_first_search(cell_map, search_map, paths_searched):
    queue = deque([{"cell": 0, "neighbors": cell_map[0]}])
    search_map[0]["searched"] = True
    while queue:
        current = queue.popleft()
        cell_idx = current["cell"]
        if cell_idx == len(cell_map) - 1:
            search_map[cell_idx]["inSolution"] = True
            backtrack(search_map, paths_searched, cell_idx)
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
                yield
    return False


def a_star_search(cell_map, search_map, paths_searched, rows, cols, choice):
    manhattan_map = []
    for r in range(rows):
        for c in range(cols):
            cost_to_exit = (rows - 1 - r) + (cols - 1 - c)
            manhattan_map.append({"costToArrive": -1, "costToExit": cost_to_exit})
    manhattan_map[0]["costToArrive"] = 0
    search_map[0]["searched"] = True
    open_list = [{"cell": 0, "neighbors": cell_map[0]}]
    while open_list:
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
        if cell_idx == len(cell_map) - 1:
            search_map[cell_idx]["inSolution"] = True
            backtrack(search_map, paths_searched, cell_idx)
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
                        yield
    return False
