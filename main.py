# main.py
import pygame
import sys
from config import (
    BLACK,
    WHITE,
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
# Start in fullscreen mode
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()
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

    # Create dropdowns for Rows and Cols - position will be calculated based on screen size
    dropdown_width = 120
    dropdown_height = 30
    dropdown_x = WINDOW_WIDTH - dropdown_width - 80
    
    # Create dropdowns with dynamic positioning
    row_dropdown = Dropdown(
        x=dropdown_x,
        y=130,
        w=dropdown_width,
        h=dropdown_height,
        font=BUTTON_FONT,
        options=[str(r) for r in ROW_OPTIONS],
        selected_index=2,
        z_index=10  # Higher z-index to ensure they appear on top
    )
    
    col_dropdown = Dropdown(
        x=dropdown_x,
        y=180,
        w=dropdown_width,
        h=dropdown_height,
        font=BUTTON_FONT,
        options=[str(c) for c in COL_OPTIONS],
        selected_index=2,
        z_index=10  # Higher z-index to ensure they appear on top
    )

    # Algorithm buttons
    button_data = [
        ("Depth-First Search", 1),
        ("Breadth-First Search", 2),
        ("A* Search - 1", 4),
        ("A* Search - 2", 5),
        ("New Maze", 0),
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

    while running:
        # Recalculate dynamic values for screen size
        WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()
        dropdown_x = WINDOW_WIDTH - dropdown_width - 80
        row_dropdown.rect.x = dropdown_x
        col_dropdown.rect.x = dropdown_x
        
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
        by = 240
        for text, mode in button_data:
            buttons.append((pygame.Rect(sidebar_x, by, button_width, button_height), text, mode))
            by += button_height + button_gap
        
        # Position speed buttons
        speed_button_width = button_width // 2 - 5
        speed_buttons_rects = []
        for i, (text, change) in enumerate(speed_buttons):
            x_pos = sidebar_x + (i * (speed_button_width + 10))
            speed_buttons_rects.append((pygame.Rect(x_pos, by, speed_button_width, button_height), text, change))
        by += button_height + button_gap
        
        # Position control buttons
        control_buttons_rects = []
        for i, (text, action) in enumerate(control_buttons):
            x_pos = sidebar_x + (i * (speed_button_width + 10))
            control_buttons_rects.append((pygame.Rect(x_pos, by, speed_button_width, button_height), text, action))
        
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
                                    else:
                                        game.start_search(mode)
                            
                            # Check speed buttons
                            for rect, text, change in speed_buttons_rects:
                                adjusted_rect = pygame.Rect(
                                    rect.x, rect.y - scroll_y, rect.width, rect.height
                                )
                                if adjusted_rect.collidepoint(mx, my):
                                    if change < 0:
                                        game.search_speed = max(1, game.search_speed // 2)
                                    else:
                                        game.search_speed = min(60, game.search_speed * 2)
                            
                            # Check control buttons
                            for rect, text, action in control_buttons_rects:
                                adjusted_rect = pygame.Rect(
                                    rect.x, rect.y - scroll_y, rect.width, rect.height
                                )
                                if adjusted_rect.collidepoint(mx, my):
                                    if action == "toggle_fullscreen":
                                        if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
                                            screen = pygame.display.set_mode(
                                                (1200, 800), pygame.RESIZABLE
                                            )
                                            WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 800
                                        else:
                                            screen = pygame.display.set_mode(
                                                (0, 0), pygame.FULLSCREEN
                                            )
                                            WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()
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
        if game.mode in [1, 2, 4, 5] and game.search_generator:
            for _ in range(game.search_speed):
                try:
                    next(game.search_generator)
                except StopIteration:
                    game.mode = 0
                    game.search_generator = None
                    break
        
        # Fill background
        screen.fill(BACKGROUND_COLOR)
        
        # Draw header
        header_height = 70
        pygame.draw.rect(screen, HEADER_COLOR, (0, 0, WINDOW_WIDTH, header_height))
        title_surf = TITLE_FONT.render("Brainy Maze", True, BLACK)
        screen.blit(title_surf, (20, 10))
        
        # Calculate maze area dimensions
        margin_left = 50
        margin_top = header_height + 30
        sidebar_width = 300
        available_w = WINDOW_WIDTH - margin_left - sidebar_width
        available_h = WINDOW_HEIGHT - margin_top - 80  # Leave room for footer
        cell_size = min(available_w // game.cols, available_h // game.rows)
        maze_width = cell_size * game.cols
        maze_height = cell_size * game.rows
        
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
        
        # Draw dropdowns
        row_dropdown.draw(screen, "Rows:", scroll_y)
        col_dropdown.draw(screen, "Cols:", scroll_y)
        
        # Draw algorithm buttons
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for rect, text, mode in buttons:
            adjusted_rect = pygame.Rect(
                rect.x, rect.y - scroll_y, rect.width, rect.height
            )
            is_hovered = adjusted_rect.collidepoint(mouse_x, mouse_y)
            draw_button(screen, adjusted_rect, text, BUTTON_FONT, is_hovered)
        
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
        
        # Draw search speed display
        speed_text = f"Search Speed: {game.search_speed}"
        speed_surf = TEXT_FONT.render(speed_text, True, BLACK)
        screen.blit(speed_surf, (sidebar_x, by + button_height + 10 - scroll_y))
        
        # Draw scrollbar if needed
        if content_height > WINDOW_HEIGHT:
            draw_scrollbar(screen, content_height, WINDOW_HEIGHT, scroll_y)
        
        # Draw footer with instructions
        footer_y = WINDOW_HEIGHT - 70
        footer_height = 70
        pygame.draw.rect(screen, HEADER_COLOR, (0, footer_y, WINDOW_WIDTH, footer_height))
        
        # Draw instructions in footer
        instr1 = TEXT_FONT.render("Use W/A/S/D or Arrow keys to move manually!", True, BLACK)
        instr2 = TEXT_FONT.render("Or click algorithm buttons to visualize search!", True, BLACK)
        screen.blit(instr1, (margin_left, footer_y + 10))
        screen.blit(instr2, (margin_left, footer_y + 40))
        
        # Draw A* search info
        note_y = margin_top + maze_height + 20 - scroll_y
        if note_y < footer_y - 100:  # Only show if there's room
            note_lines = [
                "NOTE:",
                "A* Search - 1: cost = (distance traveled) + (Manhattan distance to exit).",
                "A* Search - 2: cost = (Manhattan distance to exit) only.",
            ]
            for i, line in enumerate(note_lines):
                note_surf = SMALL_FONT.render(line, True, BLACK)
                screen.blit(note_surf, (margin_left, note_y + i * 20))
        
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()