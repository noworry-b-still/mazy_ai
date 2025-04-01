# main.py
import pygame
from config import (
    BLACK,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    TITLE_FONT,
    TEXT_FONT,
    BUTTON_FONT,
    SMALL_FONT,
    ROW_OPTIONS,
    COL_OPTIONS,
    BACKGROUND_COLOR,
    HEADER_COLOR,
)
from dropdown import Dropdown
from game import BrainyMaze
from ui_components import draw_maze, draw_scrollbar, draw_button

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Brainy Maze")
clock = pygame.time.Clock()


def main():
    global WINDOW_WIDTH, WINDOW_HEIGHT, screen
    scroll_y = 0
    max_scroll_y = 0
    running = True
    dragging_scrollbar = False

    # Create a default game with 20x20
    game = BrainyMaze(ROW_OPTIONS[2], COL_OPTIONS[2])

    # Create dropdowns for Rows and Cols
    row_dropdown = Dropdown(
        x=1000,
        y=70,
        w=80,
        h=30,
        font=BUTTON_FONT,
        options=[str(r) for r in ROW_OPTIONS],
        selected_index=2,
    )
    col_dropdown = Dropdown(
        x=1000,
        y=110,
        w=80,
        h=30,
        font=BUTTON_FONT,
        options=[str(c) for c in COL_OPTIONS],
        selected_index=2,
    )

    # Algorithm buttons
    button_data = [
        ("Depth-First Search", 1),
        ("Breadth-First Search", 2),
        ("A* Search - 1", 4),
        ("A* Search - 2", 5),
        ("New Maze", 0),
    ]
    buttons = []
    bx = 950
    by = 160
    bw = 200
    bh = 40
    gap = 10
    for text, mode in button_data:
        buttons.append((pygame.Rect(bx, by, bw, bh), text, mode))
        by += bh + gap

    # Speed control buttons
    speed_buttons = [
        (pygame.Rect(950, by, 95, bh), "Slower", -1),
        (pygame.Rect(1055, by, 95, bh), "Faster", 1),
    ]
    by += bh + gap

    while running:
        content_height = max(WINDOW_HEIGHT, 700 + game.rows * 30)
        max_scroll_y = max(0, content_height - WINDOW_HEIGHT)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode(
                    (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE
                )
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    scrollbar_x = WINDOW_WIDTH - 15
                    if mx > scrollbar_x:
                        dragging_scrollbar = True
                    else:
                        changed_row = row_dropdown.handle_event(event, scroll_y)
                        changed_col = col_dropdown.handle_event(event, scroll_y)
                        if changed_row:
                            new_rows = ROW_OPTIONS[row_dropdown.selected_index]
                            game.rows = new_rows
                            game.reset()
                        if changed_col:
                            new_cols = COL_OPTIONS[col_dropdown.selected_index]
                            game.cols = new_cols
                            game.reset()
                        for rect, text, mode in buttons:
                            adjusted_rect = pygame.Rect(
                                rect.x, rect.y - scroll_y, rect.width, rect.height
                            )
                            if adjusted_rect.collidepoint(mx, my):
                                if mode == 0:
                                    game.reset()
                                else:
                                    game.start_search(mode)
                        for rect, text, change in speed_buttons:
                            adjusted_rect = pygame.Rect(
                                rect.x, rect.y - scroll_y, rect.width, rect.height
                            )
                            if adjusted_rect.collidepoint(mx, my):
                                if change < 0:
                                    game.search_speed = max(1, game.search_speed // 2)
                                else:
                                    game.search_speed = min(60, game.search_speed * 2)
                elif event.button == 4:
                    scroll_y = max(0, scroll_y - 30)
                elif event.button == 5:
                    scroll_y = min(max_scroll_y, scroll_y + 30)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_scrollbar = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging_scrollbar:
                    _, my = event.pos
                    ratio = my / WINDOW_HEIGHT
                    scroll_y = int(ratio * max_scroll_y)
                    scroll_y = max(0, min(max_scroll_y, scroll_y))
            elif event.type == pygame.KEYDOWN:
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
        if game.mode in [1, 2, 4, 5] and game.search_generator:
            for _ in range(game.search_speed):
                try:
                    next(game.search_generator)
                except StopIteration:
                    game.mode = 0
                    game.search_generator = None
                    break
        screen.fill(
            BACKGROUND_COLOR
        )  # Alternatively, use BACKGROUND_COLOR from config if imported
        pygame.draw.rect(screen, HEADER_COLOR, (0, 0, WINDOW_WIDTH, 60))
        title_surf = TITLE_FONT.render("Brainy Maze", True, BLACK)
        screen.blit(title_surf, (20, 5))
        subtitle_surf = TEXT_FONT.render("A Pathfinding Visualization", True, BLACK)
        screen.blit(subtitle_surf, (20, 50))
        margin_left = 50
        margin_top = 80
        available_w = WINDOW_WIDTH - margin_left - 300
        available_h = WINDOW_HEIGHT - margin_top - 50
        cell_size = min(available_w // game.cols, available_h // game.rows)
        maze_width = cell_size * game.cols
        maze_height = cell_size * game.rows
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
        row_dropdown.draw(screen, "Rows:", scroll_y)
        col_dropdown.draw(screen, "Cols:", scroll_y)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for rect, text, mode in buttons:
            adjusted_rect = pygame.Rect(
                rect.x, rect.y - scroll_y, rect.width, rect.height
            )
            is_hovered = adjusted_rect.collidepoint(mouse_x, mouse_y)
            draw_button(screen, adjusted_rect, text, BUTTON_FONT, is_hovered)
        for rect, text, change in speed_buttons:
            adjusted_rect = pygame.Rect(
                rect.x, rect.y - scroll_y, rect.width, rect.height
            )
            is_hovered = adjusted_rect.collidepoint(mouse_x, mouse_y)
            draw_button(screen, adjusted_rect, text, BUTTON_FONT, is_hovered)
        draw_scrollbar(screen, content_height, WINDOW_HEIGHT, scroll_y)
        instr1 = TEXT_FONT.render(
            "Use W/A/S/D or Arrow keys to move manually!", True, BLACK
        )
        instr2 = TEXT_FONT.render(
            "Or click algorithm buttons to visualize search!", True, BLACK
        )
        screen.blit(instr1, (margin_left, WINDOW_HEIGHT - 60))
        screen.blit(instr2, (margin_left, WINDOW_HEIGHT - 35))
        note_lines = [
            "NOTE:",
            "A* Search - 1: cost = (distance traveled) + (Manhattan distance to exit).",
            "A* Search - 2: cost = (Manhattan distance to exit) only.",
        ]
        note_y = margin_top + maze_height + 20 - scroll_y
        for i, line in enumerate(note_lines):
            note_surf = SMALL_FONT.render(line, True, BLACK)
            screen.blit(note_surf, (margin_left, note_y + i * 20))
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
