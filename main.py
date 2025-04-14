# main.py
import pygame
import sys
from config import (
    BLACK,
    WHITE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    TEXT_FONT,
    BUTTON_FONT,
    SMALL_FONT,
    ROW_OPTIONS,
    COL_OPTIONS,
)
from dropdown import Dropdown
from game import MAZY_AI
from ui_components import draw_maze, draw_scrollbar, draw_button
from algorithm_comparison import compare_algorithms, show_comparison_screen

pygame.init()
# Start in fullscreen mode
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()
pygame.display.set_caption("MAZY AI")
clock = pygame.time.Clock()


def main():
    global WINDOW_WIDTH, WINDOW_HEIGHT, screen
    scroll_y = 0
    max_scroll_y = 0
    running = True
    dragging_scrollbar = False
    comparison_active = False
    comparison_results = None

    # Create a default game with 20x20
    game = MAZY_AI(ROW_OPTIONS[2], COL_OPTIONS[2])

    # Create smaller dropdowns for Rows and Cols
    dropdown_width = 70  # Smaller width
    dropdown_height = 25  # Smaller height
    dropdown_gap = 30

    # Create small font for dropdown
    small_dropdown_font = pygame.font.SysFont("Arial", 16)

    # Create dropdowns with side-by-side positioning
    row_dropdown = Dropdown(
        x=WINDOW_WIDTH - 2 * dropdown_width - dropdown_gap - 50,
        y=160,
        w=dropdown_width,
        h=dropdown_height,
        font=small_dropdown_font,  # Use smaller font
        options=[str(r) for r in ROW_OPTIONS],
        selected_index=2,
        z_index=10,
        dropdown_direction="up",  # Make the dropdown expand upward
    )

    col_dropdown = Dropdown(
        x=WINDOW_WIDTH - dropdown_width - 50,
        y=160,
        w=dropdown_width,
        h=dropdown_height,
        font=small_dropdown_font,  # Use smaller font
        options=[str(c) for c in COL_OPTIONS],
        selected_index=2,
        z_index=10,
        dropdown_direction="up",  # Make the dropdown expand upward
    )

    # Algorithm buttons
    button_data = [
        ("Depth-First Search", 1),
        ("Breadth-First Search", 2),
        ("A* Search - 1", 4),
        ("A* Search - 2", 5),
        ("Uniform-Cost Search", 6),
        ("Ant Colony Opt.", 7),
        ("New Maze", 0),
        ("Compare Algorithms", "compare"),  # New compare button
    ]

    # Speed control buttons
    speed_buttons = [
        ("Slower", -1),
        ("Faster", 1),
    ]

    # Fullscreen toggle and exit buttons
    control_buttons = [
        ("Windowed", "toggle_fullscreen"),
        ("Exit", "exit"),
    ]

    def return_from_comparison():
        nonlocal comparison_active
        comparison_active = False

    # Define color theme
    theme = {
        "header_bg": (40, 60, 80),  # Dark blue header
        "header_accent": (255, 215, 0),  # Gold accent
        "content_bg": (200, 215, 230),  # Light blue-gray background
        "button_normal": (255, 255, 255),  # White buttons
        "button_hover": (230, 240, 250),  # Light blue button hover
        "button_text": (40, 60, 80),  # Dark blue text
        "footer_bg": (60, 80, 100),  # Darker blue footer
        "footer_text": (255, 255, 255),  # White footer text
    }

    while running:
        # Handle comparison view if active
        if comparison_active:
            if comparison_results is None:
                # Run the comparison
                comparison_results = compare_algorithms(game)

            # Show the comparison screen
            show_comparison_screen(screen, comparison_results, return_from_comparison)
            comparison_active = False
            comparison_results = None
            continue

        # Recalculate dynamic values for screen size
        WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()

        # Update dropdown positions
        row_dropdown.rect.x = WINDOW_WIDTH - 2 * dropdown_width - dropdown_gap - 50
        col_dropdown.rect.x = WINDOW_WIDTH - dropdown_width - 50

        # Calculate max scroll based on content
        content_height = max(WINDOW_HEIGHT, 700 + game.rows * 20)
        max_scroll_y = max(0, content_height - WINDOW_HEIGHT)
        if scroll_y > max_scroll_y:
            scroll_y = max_scroll_y

        # Calculate button positions and sizes
        button_width = 220
        button_height = 40
        button_gap = 15
        sidebar_x = WINDOW_WIDTH - button_width - 50

        # Position algorithm buttons
        buttons = []
        by = 210  # Start buttons further down to avoid dropdown conflicts
        for text, mode in button_data:
            buttons.append(
                (pygame.Rect(sidebar_x, by, button_width, button_height), text, mode)
            )
            by += button_height + button_gap

        # Position speed buttons side by side
        speed_button_width = button_width // 2 - 5
        speed_buttons_rects = []
        for i, (text, change) in enumerate(speed_buttons):
            x_pos = sidebar_x + (i * (speed_button_width + 10))
            speed_buttons_rects.append(
                (
                    pygame.Rect(x_pos, by, speed_button_width, button_height),
                    text,
                    change,
                )
            )
        by += button_height + button_gap

        # Position control buttons side by side
        control_buttons_rects = []
        for i, (text, action) in enumerate(control_buttons):
            x_pos = sidebar_x + (i * (speed_button_width + 10))
            control_buttons_rects.append(
                (
                    pygame.Rect(x_pos, by, speed_button_width, button_height),
                    text,
                    action,
                )
            )

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                key_map = {
                    pygame.K_UP: "up",
                    pygame.K_w: "w",
                    pygame.K_LEFT: "left",
                    pygame.K_a: "a",
                    pygame.K_DOWN: "down",
                    pygame.K_s: "s",
                    pygame.K_RIGHT: "right",
                    pygame.K_d: "d",
                }
                if event.key in key_map:
                    game.manual_move(key_map[event.key])
            elif event.type == pygame.VIDEORESIZE:
                if not pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
                    WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
                    screen = pygame.display.set_mode(
                        (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE
                    )
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mx, my = event.pos

                    # Check scrollbar clicks first
                    scrollbar_x = WINDOW_WIDTH - 20
                    if mx > scrollbar_x and mx < WINDOW_WIDTH:
                        dragging_scrollbar = True
                    else:
                        # Handle dropdown events (check these first due to higher z-index)
                        changed_row = row_dropdown.handle_event(event, scroll_y)
                        changed_col = col_dropdown.handle_event(event, scroll_y)

                        if changed_row:
                            new_rows = ROW_OPTIONS[row_dropdown.selected_index]
                            game.rows = new_rows
                            game.reset()
                        elif changed_col:
                            new_cols = COL_OPTIONS[col_dropdown.selected_index]
                            game.cols = new_cols
                            game.reset()
                        else:
                            # Check algorithm buttons
                            for rect, text, mode in buttons:
                                adjusted_rect = pygame.Rect(
                                    rect.x, rect.y - scroll_y, rect.width, rect.height
                                )
                                if adjusted_rect.collidepoint(mx, my):
                                    if mode == 0:
                                        game.reset()
                                    elif mode == "compare":
                                        comparison_active = True
                                        comparison_results = None
                                    else:
                                        game.start_search(mode)

                            # Check speed buttons
                            for rect, text, change in speed_buttons_rects:
                                adjusted_rect = pygame.Rect(
                                    rect.x, rect.y - scroll_y, rect.width, rect.height
                                )
                                if adjusted_rect.collidepoint(mx, my):
                                    if change < 0:
                                        game.search_speed = max(
                                            1, game.search_speed // 2
                                        )
                                    else:
                                        game.search_speed = min(
                                            60, game.search_speed * 2
                                        )

                            # Check control buttons
                            for rect, text, action in control_buttons_rects:
                                adjusted_rect = pygame.Rect(
                                    rect.x, rect.y - scroll_y, rect.width, rect.height
                                )
                                if adjusted_rect.collidepoint(mx, my):
                                    if action == "toggle_fullscreen":
                                        if (
                                            pygame.display.get_surface().get_flags()
                                            & pygame.FULLSCREEN
                                        ):
                                            screen = pygame.display.set_mode(
                                                (1200, 800), pygame.RESIZABLE
                                            )
                                            WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 800
                                        else:
                                            screen = pygame.display.set_mode(
                                                (0, 0), pygame.FULLSCREEN
                                            )
                                            WINDOW_WIDTH, WINDOW_HEIGHT = (
                                                screen.get_size()
                                            )
                                    elif action == "exit":
                                        running = False

                elif event.button == 4:  # Mouse wheel up
                    scroll_y = max(0, scroll_y - 30)
                elif event.button == 5:  # Mouse wheel down
                    scroll_y = min(max_scroll_y, scroll_y + 30)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_scrollbar = False

            elif event.type == pygame.MOUSEMOTION:
                if dragging_scrollbar:
                    _, my = event.pos
                    if max_scroll_y > 0:  # Prevent division by zero
                        scroll_ratio = my / WINDOW_HEIGHT
                        scroll_y = int(scroll_ratio * max_scroll_y)
                        scroll_y = max(0, min(max_scroll_y, scroll_y))

        # Update automated search algorithms
        if game.mode in [1, 2, 4, 5, 6, 7] and game.search_generator:
            for _ in range(game.search_speed):
                try:
                    next(game.search_generator)
                except StopIteration:
                    game.mode = 0
                    game.search_generator = None
                    break

        # Draw gradient background
        for y in range(WINDOW_HEIGHT):
            # Calculate color for this row (linear interpolation)
            ratio = y / WINDOW_HEIGHT
            r = int(200 * (1 - ratio) + 180 * ratio)
            g = int(215 * (1 - ratio) + 195 * ratio)
            b = int(230 * (1 - ratio) + 210 * ratio)
            color = (r, g, b)

            # Draw horizontal line with this color
            pygame.draw.line(screen, color, (0, y), (WINDOW_WIDTH, y))

        # Draw header with gradient effect
        header_height = 80
        pygame.draw.rect(
            screen, theme["header_bg"], (0, 0, WINDOW_WIDTH, header_height)
        )

        # Add decorative accent line
        pygame.draw.rect(
            screen, theme["header_accent"], (0, header_height - 3, WINDOW_WIDTH, 3)
        )

        # Draw title with shadow effect
        title_surf = pygame.font.SysFont("Arial", 48, bold=True).render(
            "MAZY AI", True, WHITE
        )
        shadow_offset = 2
        shadow_surf = pygame.font.SysFont("Arial", 48, bold=True).render(
            "MAZY AI", True, (20, 30, 40)
        )
        screen.blit(shadow_surf, (25 + shadow_offset, 15 + shadow_offset))
        screen.blit(title_surf, (25, 15))

        # Calculate maze area dimensions
        margin_left = 50
        margin_top = header_height + 30
        sidebar_width = 300
        available_w = WINDOW_WIDTH - margin_left - sidebar_width
        available_h = WINDOW_HEIGHT - margin_top - 80  # Leave room for footer
        cell_size = min(available_w // game.cols, available_h // game.rows)
        maze_width = cell_size * game.cols
        maze_height = cell_size * game.rows

        # Draw maze background and border
        maze_bg = pygame.Rect(
            margin_left - 10,
            margin_top - scroll_y - 10,
            maze_width + 20,
            maze_height + 20,
        )
        pygame.draw.rect(screen, (220, 230, 240), maze_bg, border_radius=10)
        pygame.draw.rect(screen, (100, 120, 140), maze_bg, width=3, border_radius=10)

        # Draw maze
        draw_maze(
            screen,
            game.cell_map,
            game.search_map,
            game.rows,
            game.cols,
            margin_left,
            margin_top - scroll_y,
            cell_size,
        )

        # Draw settings panel background
        settings_bg = pygame.Rect(sidebar_x - 20, 140, button_width + 40, 70)
        pygame.draw.rect(screen, (220, 230, 240), settings_bg, border_radius=8)
        pygame.draw.rect(screen, (100, 120, 140), settings_bg, width=2, border_radius=8)

        # Draw dropdowns with compact labels
        row_dropdown.draw(screen, "R:", scroll_y)  # Shorter label
        col_dropdown.draw(screen, "C:", scroll_y)  # Shorter label

        # Draw algorithm buttons with enhanced style
        mouse_x, mouse_y = pygame.mouse.get_pos()

        button_colors = {
            "Depth-First Search": (220, 70, 70),  # Red
            "Breadth-First Search": (70, 100, 230),  # Blue
            "Uniform-Cost Search": (50, 200, 100),  # Green
            "A* Search - 1": (255, 140, 0),  # Orange
            "A* Search - 2": (148, 0, 211),  # Purple
            "Ant Colony Opt.": (255, 105, 180),  # Pink
            "New Maze": (60, 180, 200),  # Teal
            "Compare Algorithms": (80, 100, 160),  # Navy
        }

        # Draw buttons with colored indicators
        for rect, text, mode in buttons:
            adjusted_rect = pygame.Rect(
                rect.x, rect.y - scroll_y, rect.width, rect.height
            )
            is_hovered = adjusted_rect.collidepoint(mouse_x, mouse_y)

            # Get button color
            button_color = button_colors.get(text, (100, 100, 100))

            # Draw button with color indicator
            pygame.draw.rect(
                screen, theme["button_normal"], adjusted_rect, border_radius=6
            )
            pygame.draw.rect(
                screen, (100, 120, 140), adjusted_rect, width=1, border_radius=6
            )

            # Add colored indicator
            indicator_rect = pygame.Rect(
                adjusted_rect.x + 5, adjusted_rect.y + 5, 8, adjusted_rect.height - 10
            )
            pygame.draw.rect(screen, button_color, indicator_rect, border_radius=2)

            # Hover effect
            if is_hovered:
                hover_overlay = pygame.Rect(adjusted_rect)
                pygame.draw.rect(
                    screen,
                    (*theme["button_hover"], 128),
                    hover_overlay,
                    border_radius=6,
                )
                # Add highlight
                pygame.draw.rect(
                    screen,
                    (200, 200, 200),
                    (
                        adjusted_rect.x + 5,
                        adjusted_rect.y + adjusted_rect.height - 5,
                        adjusted_rect.width - 10,
                        3,
                    ),
                    border_radius=2,
                )

            # Button text
            text_surf = BUTTON_FONT.render(text, True, theme["button_text"])
            screen.blit(
                text_surf,
                (
                    adjusted_rect.x + 20,  # Offset to account for indicator
                    adjusted_rect.y
                    + (adjusted_rect.height - text_surf.get_height()) // 2,
                ),
            )

        # Draw speed buttons
        for rect, text, change in speed_buttons_rects:
            adjusted_rect = pygame.Rect(
                rect.x, rect.y - scroll_y, rect.width, rect.height
            )
            is_hovered = adjusted_rect.collidepoint(mouse_x, mouse_y)
            draw_button(screen, adjusted_rect, text, BUTTON_FONT, is_hovered)

        # Draw control buttons
        for rect, text, action in control_buttons_rects:
            adjusted_rect = pygame.Rect(
                rect.x, rect.y - scroll_y, rect.width, rect.height
            )
            is_hovered = adjusted_rect.collidepoint(mouse_x, mouse_y)
            draw_button(screen, adjusted_rect, text, BUTTON_FONT, is_hovered)

        # Draw search speed display with improved style
        speed_bg = pygame.Rect(
            sidebar_x - 20, by + button_height + 5 - scroll_y, button_width + 40, 40
        )
        pygame.draw.rect(screen, (220, 230, 240), speed_bg, border_radius=8)
        pygame.draw.rect(screen, (100, 120, 140), speed_bg, width=1, border_radius=8)

        speed_text = f"Search Speed: {game.search_speed}"
        speed_surf = TEXT_FONT.render(speed_text, True, BLACK)
        screen.blit(speed_surf, (sidebar_x, by + button_height + 15 - scroll_y))

        # Draw scrollbar if needed
        if content_height > WINDOW_HEIGHT:
            draw_scrollbar(screen, content_height, WINDOW_HEIGHT, scroll_y)

        # Draw footer with instructions
        footer_y = WINDOW_HEIGHT - 80
        footer_height = 80
        pygame.draw.rect(
            screen, theme["footer_bg"], (0, footer_y, WINDOW_WIDTH, footer_height)
        )

        # Draw footer accent line
        pygame.draw.rect(screen, theme["header_accent"], (0, footer_y, WINDOW_WIDTH, 3))

        # Draw instructions in footer
        instr1 = TEXT_FONT.render(
            "Use W/A/S/D or Arrow keys to move manually!", True, theme["footer_text"]
        )
        instr2 = TEXT_FONT.render(
            "Or click algorithm buttons to visualize search!",
            True,
            theme["footer_text"],
        )
        screen.blit(instr1, (margin_left, footer_y + 15))
        screen.blit(instr2, (margin_left, footer_y + 45))

        # Add copyright notice
        copyright_text = "© Dinesh Pandikona. All rights reserved 2025"
        copyright_surf = pygame.font.SysFont("Arial", 16).render(
            copyright_text, True, (200, 200, 200)
        )
        screen.blit(
            copyright_surf,
            (
                WINDOW_WIDTH - copyright_surf.get_width() - 15,
                footer_y + footer_height - 25,
            ),
        )

        # Draw A* search info as a floating info box
        note_y = margin_top + maze_height + 20 - scroll_y
        if note_y < footer_y - 100:  # Only show if there's room
            info_bg = pygame.Rect(margin_left - 10, note_y - 10, 600, 90)
            pygame.draw.rect(screen, (220, 230, 240, 200), info_bg, border_radius=8)
            pygame.draw.rect(screen, (100, 120, 140), info_bg, width=2, border_radius=8)

            note_lines = [
                "NOTE:",
                "A* Search - 1: cost = (distance traveled) + (Manhattan distance to exit).",
                "A* Search - 2: cost = (Manhattan distance to exit) only.",
            ]
            for i, line in enumerate(note_lines):
                note_surf = SMALL_FONT.render(line, True, BLACK)
                screen.blit(note_surf, (margin_left + 10, note_y + i * 25))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
