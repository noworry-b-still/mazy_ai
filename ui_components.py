# ui_components.py
import pygame
from config import (
    WHITE,
    LIGHT_CORAL,
    CORN_FLOWER_BLUE,
    BLACK,
    BACKGROUND_COLOR,
    HEADER_COLOR,
    BUTTON_HOVER,
)


def draw_maze(
    surface,
    cell_map,
    search_map,
    rows,
    cols,
    x_off,
    y_off,
    cell_size,
    y_scroll_offset=0,
):
    # Calculate the bounds of visible area to avoid drawing cells that are off-screen
    visible_top = max(0, (y_scroll_offset - y_off) // cell_size)
    visible_bottom = min(rows, (y_scroll_offset + surface.get_height() - y_off) // cell_size + 1)
    
    # Draw border around the maze
    border_width = 2
    maze_rect = pygame.Rect(
        x_off - border_width,
        y_off - border_width,
        cols * cell_size + border_width * 2,
        rows * cell_size + border_width * 2
    )
    pygame.draw.rect(surface, BLACK, maze_rect, width=border_width)
    
    # Only draw cells that are visible in the current view
    for row in range(visible_top, visible_bottom):
        for col in range(cols):
            idx = row * cols + col
            x = x_off + col * cell_size
            y = y_off + row * cell_size
            
            # Choose cell color based on state
            cell_color = WHITE  # Default cell color (unexplored)
            
            # Start cell
            if idx == 0:
                cell_color = (50, 205, 50)  # Bright green for start
            # End cell
            elif idx == rows * cols - 1:
                cell_color = (220, 20, 60)  # Crimson for end
            # Solution path cells (colored in red/light coral)
            elif search_map[idx]["inSolution"]:
                cell_color = LIGHT_CORAL
            # Searched cells (colored in blue)
            elif search_map[idx]["searched"]:
                cell_color = CORN_FLOWER_BLUE
            
            # Draw cell background
            pygame.draw.rect(surface, cell_color, (x, y, cell_size, cell_size))
            
            # Adjust wall thickness based on cell size
            line_thickness = max(1, int(cell_size / 25))
            
            # Draw walls where there's no connection
            # Left wall
            if idx % cols != 0 and not cell_map[idx].left["connection"]:
                pygame.draw.line(surface, BLACK, (x, y), (x, y + cell_size), line_thickness)
            
            # Right wall
            if (idx + 1) % cols != 0 and not cell_map[idx].right["connection"]:
                pygame.draw.line(
                    surface, BLACK, (x + cell_size, y), (x + cell_size, y + cell_size), line_thickness
                )
            
            # Top wall
            if idx >= cols and not cell_map[idx].top["connection"]:
                pygame.draw.line(surface, BLACK, (x, y), (x + cell_size, y), line_thickness)
            
            # Bottom wall
            if idx < (rows * cols - cols) and not cell_map[idx].bottom["connection"]:
                pygame.draw.line(
                    surface, BLACK, (x, y + cell_size), (x + cell_size, y + cell_size), line_thickness
                )
            
            # External walls (maze boundaries)
            if idx % cols == 0:  # Leftmost column
                pygame.draw.line(surface, BLACK, (x, y), (x, y + cell_size), line_thickness)
            if (idx + 1) % cols == 0:  # Rightmost column
                pygame.draw.line(
                    surface, BLACK, (x + cell_size, y), (x + cell_size, y + cell_size), line_thickness
                )
            if idx < cols:  # Top row
                pygame.draw.line(surface, BLACK, (x, y), (x + cell_size, y), line_thickness)
            if idx >= (rows * cols - cols):  # Bottom row
                pygame.draw.line(
                    surface, BLACK, (x, y + cell_size), (x + cell_size, y + cell_size), line_thickness
                )
            
            # Add visual markers for start and end cells
            if idx == 0:  # Start cell
                radius = max(3, cell_size // 6)
                center_x = x + cell_size // 2
                center_y = y + cell_size // 2
                pygame.draw.circle(surface, BLACK, (center_x, center_y), radius)
            elif idx == rows * cols - 1:  # End cell
                margin = max(2, cell_size // 8)
                pygame.draw.rect(
                    surface,
                    BLACK,
                    (x + margin, y + margin, cell_size - 2 * margin, cell_size - 2 * margin),
                    width=max(1, cell_size // 12)
                )


def draw_scrollbar(surface, content_height, visible_height, scroll_y):
    if content_height <= visible_height:
        return  # No need for scrollbar
    
    # Improved scrollbar design
    scrollbar_width = 15
    scrollbar_x = surface.get_width() - scrollbar_width - 5
    
    # Draw scrollbar track
    track_rect = pygame.Rect(scrollbar_x, 5, scrollbar_width, visible_height - 10)
    pygame.draw.rect(surface, (220, 220, 220), track_rect, border_radius=7)
    pygame.draw.rect(surface, (180, 180, 180), track_rect, width=1, border_radius=7)
    
    # Calculate thumb size and position
    scroll_ratio = 0
    if content_height > visible_height:
        scroll_ratio = scroll_y / (content_height - visible_height)
    
    thumb_height = max(50, (visible_height / content_height) * visible_height)
    thumb_pos = 5 + scroll_ratio * (visible_height - thumb_height - 10)
    
    # Draw scrollbar thumb
    thumb_rect = pygame.Rect(scrollbar_x, thumb_pos, scrollbar_width, thumb_height)
    pygame.draw.rect(surface, (150, 150, 150), thumb_rect, border_radius=7)
    
    # Add highlight effect
    highlight_rect = pygame.Rect(scrollbar_x + 2, thumb_pos + 2, scrollbar_width - 4, 5)
    pygame.draw.rect(surface, (180, 180, 180), highlight_rect, border_radius=3)


def draw_button(surface, rect, text, font, is_hovered):
    # Enhanced button style
    color = BUTTON_HOVER if is_hovered else WHITE
    
    # Draw button with slight gradient effect
    pygame.draw.rect(surface, color, rect, border_radius=5)
    
    # Add a subtle bottom shadow for 3D effect
    shadow_rect = pygame.Rect(rect.x, rect.y + rect.height - 2, rect.width, 2)
    pygame.draw.rect(surface, (200, 200, 200), shadow_rect, border_radius=2)
    
    # Draw border - darker when hovered
    border_color = (120, 120, 120) if is_hovered else (180, 180, 180)
    pygame.draw.rect(surface, border_color, rect, width=1, border_radius=5)
    
    # Draw text
    txt_surf = font.render(text, True, BLACK)
    surface.blit(
        txt_surf,
        (
            rect.x + (rect.width - txt_surf.get_width()) // 2,
            rect.y + (rect.height - txt_surf.get_height()) // 2,
        ),
    )
    
    # Add indicator when hovered
    if is_hovered:
        indicator_height = 3
        indicator_rect = pygame.Rect(
            rect.x + 5, 
            rect.y + rect.height - indicator_height - 2,
            rect.width - 10, 
            indicator_height
        )
        pygame.draw.rect(surface, (100, 100, 100), indicator_rect, border_radius=1)