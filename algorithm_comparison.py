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

from maze import backtrack
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


# Fix for the show_comparison_screen function to enable proper scrolling


def show_comparison_screen(screen, stats, back_callback):
    """Display a comparison screen with the algorithm statistics"""
    running = True
    scroll_y = 0
    max_scroll_y = 0
    window_width, window_height = screen.get_size()
    # Background gradient colors
    gradient_top = (220, 230, 240)  # Light blue-gray for the top of the screen
    gradient_bottom = (170, 190, 210)  # Slightly darker blue-gray for the bottom

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

    # Fixed position for back button (always visible)
    back_button = pygame.Rect(window_width - 180, window_height - 70, 150, 50)

    # Algorithm colors for visualization with improved contrast
    algorithm_colors = {
        "Depth-First Search": (220, 70, 70),  # Brighter red
        "Breadth-First Search": (70, 100, 230),  # Brighter blue
        "Uniform-Cost Search": (50, 200, 100),  # Vibrant green
        "A* Search (f = g + h)": (255, 140, 0),  # Bright orange
        "A* Search (f = h)": (148, 0, 211),  # Vivid purple
        "Ant Colony Optimization": (255, 105, 180),  # Hot pink
    }

    # Pre-calculate the total content height (important for scrolling)
    # Base calculations
    table_height = 150 + len(rows) * 40  # Header + rows
    metrics_section_height = 50  # Section title

    # Calculate bar charts height
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

    bar_height = 30
    bar_spacing = 15
    metrics_height = 0

    for _, _, _ in metrics:
        metrics_height += 45  # Metric title + spacing
        metrics_height += (bar_height + bar_spacing) * len(
            stats
        )  # Bars for each algorithm
        metrics_height += 20  # Extra space between metrics

    # Notes section height
    notes_height = 180  # Title + lines

    # Total content height
    total_content_height = (
        table_height + metrics_section_height + metrics_height + notes_height + 100
    )  # Extra padding

    # Main comparison loop
    while running:
        # Update max scroll based on calculated content height
        content_height = total_content_height
        max_scroll_y = max(0, content_height - window_height + 100)  # Add padding

        # Process events
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

                # Critical: Handle mouse wheel scrolling properly
                elif event.button == 4:  # Mouse wheel up
                    scroll_y = max(0, scroll_y - 30)

                elif event.button == 5:  # Mouse wheel down
                    scroll_y = min(max_scroll_y, scroll_y + 30)

            # Another way to handle scrolling
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # Scroll up
                    scroll_y = max(0, scroll_y - 30)
                elif event.y < 0:  # Scroll down
                    scroll_y = min(max_scroll_y, scroll_y + 30)

        # Draw gradient background
        for y in range(window_height):
            # Calculate color for this row (linear interpolation)
            ratio = y / window_height
            r = int(gradient_top[0] * (1 - ratio) + gradient_bottom[0] * ratio)
            g = int(gradient_top[1] * (1 - ratio) + gradient_bottom[1] * ratio)
            b = int(gradient_top[2] * (1 - ratio) + gradient_bottom[2] * ratio)
            color = (r, g, b)

            # Draw horizontal line with this color
            pygame.draw.line(screen, color, (0, y), (window_width, y))

        # Draw fixed header (doesn't scroll)
        header_height = 80
        pygame.draw.rect(screen, (40, 60, 80), (0, 0, window_width, header_height))

        # Add a decorative header line
        pygame.draw.rect(screen, (255, 215, 0), (0, header_height - 3, window_width, 3))

        # Draw title with shadow effect
        title_text = "Algorithm Comparison Results"
        shadow_offset = 2

        # Shadow
        shadow_surf = pygame.font.SysFont("Arial", 36, bold=True).render(
            title_text, True, (20, 30, 40)
        )
        screen.blit(shadow_surf, (20 + shadow_offset, 20 + shadow_offset))

        # Main text
        title_surf = pygame.font.SysFont("Arial", 36, bold=True).render(
            title_text, True, (255, 255, 255)
        )
        screen.blit(title_surf, (20, 20))

        # Draw scrollable content
        content_y = header_height + 20 - scroll_y

        # Table background
        table_width = sum(col_widths) + 100
        table_height = 50 + len(rows) * 40 + 20
        table_rect = pygame.Rect(50, content_y, table_width, table_height)
        pygame.draw.rect(screen, (230, 240, 250, 200), table_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 120, 140), table_rect, width=2, border_radius=10)

        # Draw table header with background
        header_bg = pygame.Rect(50, content_y, table_width, 40)
        pygame.draw.rect(screen, (60, 90, 120), header_bg, border_radius=10)

        x_offset = 60
        header_y = content_y + 10
        for i, header in enumerate(headers):
            header_surf = pygame.font.SysFont("Arial", 22, bold=True).render(
                header, True, WHITE
            )
            screen.blit(header_surf, (x_offset, header_y))
            x_offset += col_widths[i]

        # Draw separator line
        pygame.draw.line(
            screen,
            (180, 190, 200),
            (60, header_y + 30),
            (table_width - 20, header_y + 30),
            2,
        )

        # Draw table rows with alternating background colors
        row_y = header_y + 50
        for idx, row in enumerate(rows):
            # Skip if row is outside visible area (optimization)
            if row_y + 30 < header_height or row_y > window_height:
                row_y += 40
                continue

            # Alternating row background
            row_color = (240, 245, 255) if idx % 2 == 0 else (225, 235, 245)
            row_rect = pygame.Rect(60, row_y - 5, table_width - 20, 30)
            pygame.draw.rect(screen, row_color, row_rect, border_radius=5)

            # Algorithm-colored indicator
            algo_name = row[0]
            indicator_color = algorithm_colors.get(algo_name, (150, 150, 150))
            pygame.draw.rect(
                screen, indicator_color, (60, row_y - 5, 8, 30), border_radius=2
            )

            x_offset = 60
            for i, cell in enumerate(row):
                text_color = (
                    BLACK if i > 0 else indicator_color
                )  # Make algorithm name match its color
                cell_surf = SMALL_FONT.render(cell, True, text_color)

                # Bold the first column (algorithm names)
                if i == 0:
                    cell_surf = pygame.font.SysFont("Arial", 18, bold=True).render(
                        cell, True, text_color
                    )

                screen.blit(cell_surf, (x_offset + 15 if i == 0 else x_offset, row_y))
                x_offset += col_widths[i]

            row_y += 40

        # Performance Analysis section
        analysis_y = row_y + 30

        # Add section title with decorative accent
        section_bg = pygame.Rect(50, analysis_y - 10, 350, 40)
        pygame.draw.rect(screen, (60, 90, 120), section_bg, border_radius=10)
        title_surf = pygame.font.SysFont("Arial", 24, bold=True).render(
            "Performance Analysis", True, WHITE
        )
        screen.blit(title_surf, (60, analysis_y))
        analysis_y += 50

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

        bar_height = 30
        bar_spacing = 15
        name_width = 300  # Width for algorithm names

        for metric_name, metric_func, higher_better in metrics:
            # Skip if this section is outside visible area (optimization)
            if (
                analysis_y > window_height + 100
                or analysis_y + 60 + len(stats) * (bar_height + bar_spacing)
                < header_height
            ):
                # Just update position and skip drawing
                analysis_y += 45 + (bar_height + bar_spacing) * len(stats) + 20
                continue

            # Draw metric header with background
            metric_header_bg = pygame.Rect(50, analysis_y - 10, 400, 35)
            pygame.draw.rect(screen, (80, 100, 130), metric_header_bg, border_radius=8)

            metric_surf = pygame.font.SysFont("Arial", 20, bold=True).render(
                metric_name, True, WHITE
            )
            screen.blit(metric_surf, (60, analysis_y))
            analysis_y += 45

            # Sort algorithms by this metric
            sorted_stats = sorted(stats, key=metric_func, reverse=higher_better)

            # Calculate max value for scaling
            max_value = max(metric_func(s) for s in stats) if stats else 1
            if max_value == 0:
                max_value = 1  # Avoid division by zero

            # Draw bars for each algorithm
            for i, stat in enumerate(sorted_stats):
                # Skip if this bar is outside visible area
                if (
                    analysis_y > window_height + 50
                    or analysis_y + bar_height < header_height
                ):
                    analysis_y += bar_height + bar_spacing
                    continue

                value = metric_func(stat)
                bar_length = int((value / max_value) * (window_width - 500))

                # Background for this bar row
                row_bg = pygame.Rect(
                    60, analysis_y - 5, window_width - 120, bar_height + 10
                )
                bg_color = (240, 245, 255) if i % 2 == 0 else (225, 235, 245)
                pygame.draw.rect(screen, bg_color, row_bg, border_radius=6)

                # Draw ranking and algorithm name
                algorithm_color = algorithm_colors.get(
                    stat.algorithm_name, (150, 150, 150)
                )
                rank_surf = pygame.font.SysFont("Arial", 18, bold=True).render(
                    f"{i+1}. {stat.algorithm_name}", True, algorithm_color
                )
                screen.blit(
                    rank_surf,
                    (80, analysis_y + (bar_height - rank_surf.get_height()) // 2),
                )

                # Draw bar with gradient effect
                bar_rect = pygame.Rect(name_width, analysis_y, bar_length, bar_height)
                r, g, b = algorithm_color

                # Gradient effect (darker to lighter)
                for x in range(bar_length):
                    gradient_ratio = x / max(1, bar_length)
                    # Brighten color as we move right
                    color = (
                        min(255, int(r + (255 - r) * gradient_ratio * 0.5)),
                        min(255, int(g + (255 - g) * gradient_ratio * 0.5)),
                        min(255, int(b + (255 - b) * gradient_ratio * 0.5)),
                    )
                    pygame.draw.line(
                        screen,
                        color,
                        (name_width + x, analysis_y),
                        (name_width + x, analysis_y + bar_height),
                    )

                # Bar outline
                pygame.draw.rect(
                    screen, (100, 100, 100), bar_rect, width=1, border_radius=4
                )

                # Draw value with contrasting background for readability
                value_text = f"{value:.4f}" if isinstance(value, float) else str(value)
                value_surf = pygame.font.SysFont("Arial", 18, bold=True).render(
                    value_text, True, BLACK
                )

                # Value background (white rounded rectangle)
                text_bg_rect = pygame.Rect(
                    name_width + bar_length + 10,
                    analysis_y + (bar_height - value_surf.get_height()) // 2 - 2,
                    value_surf.get_width() + 10,
                    value_surf.get_height() + 4,
                )
                pygame.draw.rect(screen, (255, 255, 255), text_bg_rect, border_radius=4)
                pygame.draw.rect(
                    screen, (200, 200, 200), text_bg_rect, width=1, border_radius=4
                )

                # Draw value text
                screen.blit(
                    value_surf,
                    (
                        name_width + bar_length + 15,
                        analysis_y + (bar_height - value_surf.get_height()) // 2,
                    ),
                )

                analysis_y += bar_height + bar_spacing

            analysis_y += 20  # Extra space between metrics

        # Draw analysis explanation with enhanced visual style
        # Skip if out of view
        if analysis_y < window_height + 200 and analysis_y + 180 > header_height:
            explanation_bg = pygame.Rect(50, analysis_y - 10, window_width - 100, 180)
            pygame.draw.rect(
                screen, (230, 240, 250, 200), explanation_bg, border_radius=10
            )
            pygame.draw.rect(
                screen, (100, 120, 140), explanation_bg, width=2, border_radius=10
            )

            explanation_title = pygame.font.SysFont("Arial", 22, bold=True).render(
                "Performance Notes:", True, (60, 90, 120)
            )
            screen.blit(explanation_title, (70, analysis_y))
            analysis_y += 35

            explanation_lines = [
                "• Breadth-First Search and Uniform-Cost Search always find the shortest path.",
                "• Depth-First Search is memory efficient but may find longer paths.",
                "• A* Search balances exploration with optimal path finding.",
                "• Ant Colony Optimization improves with multiple iterations.",
                "• Memory usage shows maximum simultaneous nodes stored.",
            ]

            for line in explanation_lines:
                line_surf = pygame.font.SysFont("Arial", 18).render(
                    line, True, (40, 40, 40)
                )
                screen.blit(line_surf, (70, analysis_y))
                analysis_y += 28

        # Draw back button (always visible, fixed position)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_back_hovered = back_button.collidepoint(mouse_x, mouse_y)

        # Draw back button with gradient
        button_color = (50, 120, 200) if is_back_hovered else (60, 100, 160)
        pygame.draw.rect(screen, button_color, back_button, border_radius=8)

        # Add button highlight
        highlight_rect = pygame.Rect(
            back_button.x + 2, back_button.y + 2, back_button.width - 4, 5
        )
        pygame.draw.rect(screen, (100, 160, 255), highlight_rect, border_radius=2)

        # Add button shadow
        shadow_rect = pygame.Rect(
            back_button.x + 2,
            back_button.y + back_button.height - 7,
            back_button.width - 4,
            5,
        )
        pygame.draw.rect(screen, (40, 80, 140), shadow_rect, border_radius=2)

        # Button text
        button_text = BUTTON_FONT.render("Back to Maze", True, WHITE)
        screen.blit(
            button_text,
            (
                back_button.x + (back_button.width - button_text.get_width()) // 2,
                back_button.y
                + (back_button.height - button_text.get_height()) // 2
                - 2,
            ),
        )

        # Draw scrollbar if needed
        if content_height > window_height:
            # Make scrollbar more visible
            scrollbar_width = 15
            scrollbar_x = window_width - scrollbar_width - 10

            # Draw track
            track_rect = pygame.Rect(
                scrollbar_x,
                header_height,
                scrollbar_width,
                window_height - header_height - 20,
            )
            pygame.draw.rect(screen, (200, 210, 220), track_rect, border_radius=7)

            # Calculate thumb size and position
            scroll_ratio = scroll_y / max_scroll_y if max_scroll_y > 0 else 0
            thumb_height = max(
                50, (window_height / content_height) * (window_height - header_height)
            )
            thumb_pos = header_height + scroll_ratio * (
                window_height - header_height - thumb_height - 20
            )

            # Draw thumb
            thumb_rect = pygame.Rect(
                scrollbar_x, thumb_pos, scrollbar_width, thumb_height
            )
            pygame.draw.rect(screen, (100, 130, 160), thumb_rect, border_radius=7)
            pygame.draw.rect(
                screen, (80, 100, 120), thumb_rect, width=1, border_radius=7
            )

        pygame.display.flip()
        # Add copyright notice (fixed at the bottom of the screen)
        copyright_text = "© Dinesh Pandikona. All rights reserved 2025"
        copyright_surf = pygame.font.SysFont("Arial", 16).render(
            copyright_text, True, (200, 200, 200)
        )
        screen.blit(
            copyright_surf,
            (window_width - copyright_surf.get_width() - 15, window_height - 25),
        )

    return True
