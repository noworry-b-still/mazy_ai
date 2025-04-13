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
        # Mark start cell as searched but not part of solution initially
        self.search_map[0]["searched"] = True

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
        """Handle manual movement through the maze."""
        if self.mode != MODE_MANUAL:
            # Initialize for manual mode if we weren't in it before
            self.initialize_search()
            self.mode = MODE_MANUAL
            self.search_map[0]["searched"] = True

        if not self.work_list:
            return

        # Get the current cell we're on
        last_cell = self.work_list[-1]
        last_idx = last_cell["cell"]
        neighbors = last_cell["neighbors"]
        exit_idx = self.rows * self.cols - 1

        # Determine which direction to move based on key
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
            return  # Invalid move, no connection in that direction

        if moved and neighbor_idx != -1:
            # Check if we're moving to a cell we've already visited
            if self.search_map[neighbor_idx]["searched"]:
                # We're backtracking - Check if it's the previous cell in our path
                if (
                    len(self.work_list) > 1
                    and self.work_list[-2]["cell"] == neighbor_idx
                ):
                    # Valid backtracking - remove current cell from the work list
                    backtracked_cell = self.work_list.pop()
                    # Clear the "searched" flag for the cell we're leaving
                    self.search_map[backtracked_cell["cell"]]["searched"] = False
                    self.search_map[backtracked_cell["cell"]]["inSolution"] = False

                    # Also remove this path from paths_searched
                    for i in range(len(self.paths_searched) - 1, -1, -1):
                        if self.paths_searched[i]["to"] == backtracked_cell["cell"]:
                            self.paths_searched.pop(i)
                            break
                # If not a direct previous cell, don't allow the move
            else:
                # We're moving to a new unvisited cell
                # Mark it as searched (blue)
                self.search_map[neighbor_idx]["searched"] = True
                # Add to our path
                self.work_list.append(
                    {"cell": neighbor_idx, "neighbors": self.cell_map[neighbor_idx]}
                )
                # Track this path for potential solution reconstruction
                self.paths_searched.append({"from": last_idx, "to": neighbor_idx})

            # Check if we've reached the exit
            if neighbor_idx == exit_idx:
                # We've reached the destination, highlight the solution path
                # Clear all solution flags first
                for i in range(len(self.search_map)):
                    self.search_map[i]["inSolution"] = False

                # Use backtrack to highlight the path from start to exit
                self.search_map[exit_idx]["inSolution"] = True
                backtrack(self.search_map, self.paths_searched, exit_idx)
                self.mode = MODE_IDLE  # Done with manual mode
