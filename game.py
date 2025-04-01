# game.py
from maze import (
    generate_cells,
    select_paths,
    depth_first_search,
    breadth_first_search,
    a_star_search,
    backtrack,
)
from config import MODE_IDLE, MODE_DFS, MODE_BFS, MODE_MANUAL, MODE_A1, MODE_A2


class BrainyMaze:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.build_maze()
        self.search_map = [
            {"searched": False, "inSolution": False}
            for _ in range(self.rows * self.cols)
        ]
        self.paths_searched = []
        self.work_list = []
        self.mode = MODE_IDLE
        self.search_generator = None
        self.search_speed = 10  # Lower is slower

    def build_maze(self):
        self.cell_map = generate_cells(self.rows, self.cols)
        select_paths(self.cell_map, self.rows, self.cols)

    def reset(self):
        self.build_maze()
        self.search_map = [
            {"searched": False, "inSolution": False}
            for _ in range(self.rows * self.cols)
        ]
        self.paths_searched = []
        self.work_list = []
        self.mode = MODE_IDLE
        self.search_generator = None

    def initialize_search(self):
        self.work_list = [{"cell": 0, "neighbors": self.cell_map[0]}]
        self.search_map = [
            {"searched": False, "inSolution": False}
            for _ in range(self.rows * self.cols)
        ]
        self.paths_searched = []

    def start_search(self, mode):
        self.initialize_search()
        self.mode = mode
        if mode == MODE_DFS:
            self.search_generator = depth_first_search(
                self.cell_map, self.search_map, self.paths_searched
            )
        elif mode == MODE_BFS:
            self.search_generator = breadth_first_search(
                self.cell_map, self.search_map, self.paths_searched
            )
        elif mode == MODE_A1:
            self.search_generator = a_star_search(
                self.cell_map,
                self.search_map,
                self.paths_searched,
                self.rows,
                self.cols,
                1,
            )
        elif mode == MODE_A2:
            self.search_generator = a_star_search(
                self.cell_map,
                self.search_map,
                self.paths_searched,
                self.rows,
                self.cols,
                2,
            )

    def manual_move(self, key):
        if self.mode != MODE_MANUAL:
            self.initialize_search()
            self.mode = MODE_MANUAL
            self.search_map[0]["searched"] = True
        if not self.work_list:
            return
        last_cell = self.work_list[-1]
        last_idx = last_cell["cell"]
        neighbors = last_cell["neighbors"]
        exit_idx = self.rows * self.cols - 1
        moved = False
        neighbor_idx = -1
        if (key == "up" or key == "w") and neighbors.top["connection"]:
            neighbor_idx = neighbors.top["neighborIndex"]
            moved = True
        elif (key == "left" or key == "a") and neighbors.left["connection"]:
            neighbor_idx = neighbors.left["neighborIndex"]
            moved = True
        elif (key == "down" or key == "s") and neighbors.bottom["connection"]:
            neighbor_idx = neighbors.bottom["neighborIndex"]
            moved = True
        elif (key == "right" or key == "d") and neighbors.right["connection"]:
            neighbor_idx = neighbors.right["neighborIndex"]
            moved = True
        else:
            return
        if moved and neighbor_idx != -1:
            if self.search_map[neighbor_idx]["searched"]:
                self.search_map[last_idx]["inSolution"] = False
                self.work_list.pop()
            else:
                self.search_map[neighbor_idx]["searched"] = True
                self.work_list.append(
                    {"cell": neighbor_idx, "neighbors": self.cell_map[neighbor_idx]}
                )
                self.paths_searched.append({"from": last_idx, "to": neighbor_idx})
            if neighbor_idx == exit_idx:
                self.search_map[exit_idx]["inSolution"] = True
                backtrack(self.search_map, self.paths_searched, exit_idx)
                self.mode = MODE_IDLE
