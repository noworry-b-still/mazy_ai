# algorithm_comparison.py
import pygame
import copy
import time
from config import (
    MODE_DFS,
    MODE_BFS,
    MODE_UCS,
    MODE_A1,
    MODE_A2,
    MODE_ACO,
    BLACK,
    WHITE,
    BACKGROUND_COLOR,
    HEADER_COLOR,
    TEXT_FONT,
    BUTTON_FONT,
    SMALL_FONT,
)

from maze import (
    backtrack,
    depth_first_search,
    breadth_first_search,
    a_star_search,
    uniform_cost_search,
    ant_colony_optimization,
)
from stats import AlgorithmStats, calculate_path_length
from ui_components import draw_button, draw_scrollbar


def run_algorithm_with_stats(game, algorithm_name, mode):
    """Run an algorithm and collect statistics"""
    # Create deep copies to avoid modifying the original maze
    cell_map = copy.deepcopy(game.cell_map)
    search_map = [
        {"searched": False, "inSolution": False} for _ in range(game.rows * game.cols)
    ]
    paths_searched = []

    # Create and initialize stats object
    stats = AlgorithmStats(algorithm_name)
    stats.start_timer()

    # Use direct implementation instead of relying on algorithm generators
    cells_explored = 0
    max_frontier_size = 0

    try:
        # Run a simplified version of each algorithm for stats collection
        if mode == MODE_DFS:
            # Depth-First Search implementation
            stack = [{"cell": 0, "neighbors": cell_map[0]}]
            search_map[0]["searched"] = True

            while stack:
                max_frontier_size = max(max_frontier_size, len(stack))
                current = stack.pop()
                cell_idx = current["cell"]
                cells_explored += 1

                if cell_idx == game.rows * game.cols - 1:  # Reached end
                    search_map[cell_idx]["inSolution"] = True
                    backtrack(search_map, paths_searched, cell_idx)
                    break

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

        elif mode == MODE_BFS:
            # Breadth-First Search implementation
            from collections import deque

            queue = deque([{"cell": 0, "neighbors": cell_map[0]}])
            search_map[0]["searched"] = True

            while queue:
                max_frontier_size = max(max_frontier_size, len(queue))
                current = queue.popleft()
                cell_idx = current["cell"]
                cells_explored += 1

                if cell_idx == game.rows * game.cols - 1:  # Reached end
                    search_map[cell_idx]["inSolution"] = True
                    backtrack(search_map, paths_searched, cell_idx)
                    break

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

        elif mode == MODE_UCS:
            # Uniform-Cost Search implementation
            import heapq

            pq = [(0, 0, {"cell": 0, "neighbors": cell_map[0]})]
            search_map[0]["searched"] = True
            cost_so_far = {0: 0}

            while pq:
                max_frontier_size = max(max_frontier_size, len(pq))
                current_cost, _, current = heapq.heappop(pq)
                cell_idx = current["cell"]
                cells_explored += 1

                if cell_idx == game.rows * game.cols - 1:  # Reached end
                    search_map[cell_idx]["inSolution"] = True
                    backtrack(search_map, paths_searched, cell_idx)
                    break

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

        elif mode == MODE_A1 or mode == MODE_A2:
            # A* Search implementation
            choice = 1 if mode == MODE_A1 else 2

            # Create Manhattan distance map
            manhattan_map = []
            for r in range(game.rows):
                for c in range(game.cols):
                    cost_to_exit = (game.rows - 1 - r) + (game.cols - 1 - c)
                    manhattan_map.append(
                        {"costToArrive": -1, "costToExit": cost_to_exit}
                    )
            manhattan_map[0]["costToArrive"] = 0

            open_list = [{"cell": 0, "neighbors": cell_map[0]}]
            search_map[0]["searched"] = True

            while open_list:
                max_frontier_size = max(max_frontier_size, len(open_list))

                # Find node with lowest f-cost
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

                if cell_idx == game.rows * game.cols - 1:  # Reached end
                    search_map[cell_idx]["inSolution"] = True
                    backtrack(search_map, paths_searched, cell_idx)
                    break

                neighbors = current["neighbors"]
                for direction in ["left", "right", "top", "bottom"]:
                    n_idx = getattr(neighbors, direction)["neighborIndex"]
                    if n_idx != -1 and getattr(neighbors, direction)["connection"]:
                        current_cost = manhattan_map[cell_idx]["costToArrive"]
                        neighbor_cost = manhattan_map[n_idx]["costToArrive"]
                        if neighbor_cost == -1 or neighbor_cost > current_cost + 1:
                            manhattan_map[n_idx]["costToArrive"] = current_cost + 1
                            if not search_map[n_idx]["searched"]:
                                open_list.append(
                                    {"cell": n_idx, "neighbors": cell_map[n_idx]}
                                )
                                paths_searched.append({"from": cell_idx, "to": n_idx})
                                search_map[n_idx]["searched"] = True

        elif mode == MODE_ACO:
            # Ant Colony Optimization (simplified)
            num_ants = 5  # Reduced for speed
            num_iterations = 3

            exit_idx = game.rows * game.cols - 1
            exit_row = exit_idx // game.cols
            exit_col = exit_idx % game.cols

            def get_heuristic(idx):
                row = idx // game.cols
                col = idx % game.cols
                return abs(row - exit_row) + abs(col - exit_col)

            # Initialize pheromone
            pheromone = {}
            for i in range(len(cell_map)):
                neighbors = cell_map[i]
                for direction in ["left", "right", "top", "bottom"]:
                    n_idx = getattr(neighbors, direction)["neighborIndex"]
                    if n_idx != -1 and getattr(neighbors, direction)["connection"]:
                        pheromone[(i, n_idx)] = 0.1

            best_path = None
            best_path_length = float("inf")

            # Loop through iterations
            for _ in range(num_iterations):
                for _ in range(num_ants):
                    current_node = 0
                    path = [current_node]
                    visited = {0: True}

                    # Ant moves until it reaches exit or gets stuck
                    while current_node != exit_idx:
                        cells_explored += 1
                        neighbors = cell_map[current_node]
                        possible_moves = []

                        # Find possible moves
                        for direction in ["left", "right", "top", "bottom"]:
                            n_idx = getattr(neighbors, direction)["neighborIndex"]
                            if (
                                n_idx != -1
                                and getattr(neighbors, direction)["connection"]
                                and n_idx not in visited
                            ):
                                possible_moves.append(n_idx)

                        if not possible_moves:
                            # No valid moves, try to backtrack
                            if len(path) > 1:
                                path.pop()
                                current_node = path[-1]
                                continue
                            else:
                                break

                        # Choose next move (simplified)
                        next_node = min(possible_moves, key=get_heuristic)
                        path.append(next_node)
                        visited[next_node] = True
                        current_node = next_node

                        if not search_map[next_node]["searched"]:
                            search_map[next_node]["searched"] = True
                            paths_searched.append({"from": path[-2], "to": next_node})

                    max_frontier_size = max(max_frontier_size, len(visited))

                    # If path found, update best path
                    if current_node == exit_idx:
                        path_length = len(path) - 1
                        if path_length < best_path_length:
                            best_path = path
                            best_path_length = path_length

            # Mark solution path if found
            if best_path:
                for node in best_path:
                    search_map[node]["inSolution"] = True

        # Populate stats with collected data
        stats.cells_explored = cells_explored
        stats.max_frontier_size = max_frontier_size
        stats.path_length = calculate_path_length(paths_searched)
        stats.stop_timer()

        print(f"Algorithm: {stats.algorithm_name}")
        print(f"  Cells explored: {stats.cells_explored}")
        print(f"  Max frontier: {stats.max_frontier_size}")
        print(f"  Path length: {stats.path_length}")
        print(f"  Time: {stats.execution_time:.4f}s")

        return stats

    except Exception as e:
        print(f"Error running {algorithm_name}: {str(e)}")
        stats.stop_timer()
        return stats


def compare_algorithms(game):
    """Run all algorithms on the current maze and collect statistics"""
    algorithms = [
        ("Depth-First Search", MODE_DFS),
        ("Breadth-First Search", MODE_BFS),
        ("Uniform-Cost Search", MODE_UCS),
        ("A* Search (f = g + h)", MODE_A1),
        ("A* Search (f = h)", MODE_A2),
        ("Ant Colony Optimization", MODE_ACO),
    ]

    stats = []
    for name, mode in algorithms:
        print(f"Running {name}...")  # Debug output
        try:
            stat = run_algorithm_with_stats(game, name, mode)
            if stat and hasattr(stat, "cells_explored"):
                stats.append(stat)
                print(f"  Collected stats for {name}")
            else:
                print(f"  Failed to collect stats for {name}")
        except Exception as e:
            print(f"Error running {name}: {str(e)}")

    print(f"Total stats collected: {len(stats)}")  # Debug output
    return stats


def create_comparison_table(stats):
    """Create a formatted table for the stats"""
    headers = ["Algorithm", "Cells Explored", "Max Memory", "Path Length", "Time (s)"]
    rows = []

    for stat in stats:
        rows.append(
            [
                stat.algorithm_name,
                str(stat.cells_explored),
                str(stat.max_frontier_size),
                str(stat.path_length),
                f"{stat.execution_time:.4f}",
            ]
        )

    return headers, rows


def get_algorithm_colors():
    """Return colors for each algorithm for consistent visualization"""
    return {
        "Depth-First Search": (255, 100, 100),  # Red
        "Breadth-First Search": (100, 100, 255),  # Blue
        "Uniform-Cost Search": (100, 255, 100),  # Green
        "A* Search (f = g + h)": (255, 165, 0),  # Orange
        "A* Search (f = h)": (128, 0, 128),  # Purple
        "Ant Colony Optimization": (255, 192, 203),  # Pink
    }


def show_comparison_screen(screen, stats, back_callback):
    """Display a comparison screen with the algorithm statistics"""
    running = True
    scroll_y = 0
    max_scroll_y = 0
    window_width, window_height = screen.get_size()

    # Check if we have valid stats to display
    if not stats or len(stats) == 0:
        # Show error message and return
        screen.fill(BACKGROUND_COLOR)
        error_surf = TEXT_FONT.render("No comparison data available", True, BLACK)
        screen.blit(
            error_surf,
            (window_width // 2 - error_surf.get_width() // 2, window_height // 2 - 20),
        )

        # Add back button
        back_button = pygame.Rect(
            window_width // 2 - 60, window_height // 2 + 20, 120, 40
        )
        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_hovered = back_button.collidepoint(mouse_x, mouse_y)
        draw_button(screen, back_button, "Back", BUTTON_FONT, is_hovered)

        pygame.display.flip()

        # Wait for user to click back or press escape
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and back_button.collidepoint(event.pos):
                        waiting = False

        back_callback()
        return

    # Create table data
    headers, rows = create_comparison_table(stats)

    # Calculate column widths
    col_widths = [
        max(len(headers[i]), max(len(row[i]) for row in rows))
        for i in range(len(headers))
    ]
    col_widths = [
        width * 12 + 50 for width in col_widths
    ]  # Scale by font width with padding

    # Button for returning
    back_button = pygame.Rect(window_width - 150, window_height - 60, 120, 40)

    # Main comparison loop
    while running:
        # Calculate content height for scrolling
        content_height = (
            150 + len(rows) * 30 + 300
        )  # Base height + rows + analysis section
        max_scroll_y = max(0, content_height - window_height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    back_callback()
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mx, my = event.pos
                    if back_button.collidepoint(mx, my):
                        running = False
                        back_callback()
                        return
                elif event.button == 4:  # Mouse wheel up
                    scroll_y = max(0, scroll_y - 30)
                elif event.button == 5:  # Mouse wheel down
                    scroll_y = min(max_scroll_y, scroll_y + 30)

        # Fill background
        screen.fill(BACKGROUND_COLOR)

        # Draw header
        header_height = 70
        pygame.draw.rect(screen, HEADER_COLOR, (0, 0, window_width, header_height))
        title_surf = TEXT_FONT.render("Algorithm Comparison Results", True, BLACK)
        screen.blit(title_surf, (20, 20))

        # Draw the back button
        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_back_hovered = back_button.collidepoint(mouse_x, mouse_y)
        draw_button(screen, back_button, "Back to Maze", BUTTON_FONT, is_back_hovered)

        # Main content area (with scroll offset)
        content_y = 100 - scroll_y

        # Draw table header
        x_offset = 50
        header_y = content_y
        for i, header in enumerate(headers):
            header_surf = BUTTON_FONT.render(header, True, BLACK)
            screen.blit(header_surf, (x_offset, header_y))
            x_offset += col_widths[i]

        # Draw separator line
        pygame.draw.line(
            screen, BLACK, (50, header_y + 30), (window_width - 50, header_y + 30), 2
        )

        # Draw table rows
        row_y = header_y + 50
        for row in rows:
            x_offset = 50
            for i, cell in enumerate(row):
                cell_surf = SMALL_FONT.render(cell, True, BLACK)
                screen.blit(cell_surf, (x_offset, row_y))
                x_offset += col_widths[i]
            row_y += 30

        # Draw horizontal separator
        pygame.draw.line(screen, BLACK, (50, row_y), (window_width - 50, row_y), 1)
        row_y += 30

        # Draw performance analysis section
        analysis_y = row_y
        title_surf = BUTTON_FONT.render("Performance Analysis", True, BLACK)
        screen.blit(title_surf, (50, analysis_y))
        analysis_y += 40

        # Draw comparisons for each metric
        metrics = [
            ("Cells Explored (lower is better)", lambda s: s.cells_explored, False),
            (
                "Max Memory Usage (lower is better)",
                lambda s: s.max_frontier_size,
                False,
            ),
            ("Path Length (lower is better)", lambda s: s.path_length, False),
            ("Execution Time (lower is better)", lambda s: s.execution_time, False),
        ]

        algorithm_colors = get_algorithm_colors()
        bar_height = 25
        bar_spacing = 10

        for metric_name, metric_func, higher_better in metrics:
            # Draw metric title
            metric_surf = SMALL_FONT.render(metric_name, True, BLACK)
            screen.blit(metric_surf, (50, analysis_y))
            analysis_y += 30

            # Sort algorithms by this metric
            sorted_stats = sorted(stats, key=metric_func, reverse=higher_better)

            # Calculate max value for scaling
            max_value = max(metric_func(s) for s in stats) if stats else 1
            if max_value == 0:
                max_value = 1  # Avoid division by zero

            # Draw bars for each algorithm
            for i, stat in enumerate(sorted_stats):
                value = metric_func(stat)
                bar_length = int((value / max_value) * (window_width - 300))

                # Draw ranking and algorithm name
                rank_surf = SMALL_FONT.render(
                    f"{i+1}. {stat.algorithm_name}", True, BLACK
                )
                screen.blit(rank_surf, (70, analysis_y))

                # Draw bar
                color = algorithm_colors.get(stat.algorithm_name, (150, 150, 150))
                pygame.draw.rect(
                    screen, color, (250, analysis_y, bar_length, bar_height)
                )

                # Draw value
                if isinstance(value, float):
                    value_text = f"{value:.4f}"
                else:
                    value_text = str(value)
                value_surf = SMALL_FONT.render(value_text, True, BLACK)
                screen.blit(value_surf, (260 + bar_length, analysis_y + 5))

                analysis_y += bar_height + bar_spacing

            analysis_y += 20  # Extra space between metrics

        # Draw analysis explanation
        analysis_y += 10
        explanation_lines = [
            "Performance Notes:",
            "• Breadth-First Search and Uniform-Cost Search always find the shortest path.",
            "• Depth-First Search is memory efficient but may find longer paths.",
            "• A* Search balances exploration with optimal path finding.",
            "• Ant Colony Optimization improves with multiple iterations.",
            "• Memory usage shows maximum simultaneous nodes stored.",
        ]

        for line in explanation_lines:
            line_surf = SMALL_FONT.render(line, True, BLACK)
            screen.blit(line_surf, (50, analysis_y))
            analysis_y += 25

        # Draw scrollbar if needed
        if content_height > window_height:
            draw_scrollbar(screen, content_height, window_height, scroll_y)

        pygame.display.flip()

    return True
