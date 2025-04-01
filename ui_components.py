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
    y_off -= y_scroll_offset
    for row in range(rows):
        for col in range(cols):
            idx = row * cols + col
            x = x_off + col * cell_size
            y = y_off + row * cell_size
            if y + cell_size < 0 or y > surface.get_height():
                continue
            color = WHITE
            if idx == 0 or idx == rows * cols - 1:
                color = LIGHT_CORAL
            elif search_map[idx]["inSolution"]:
                color = LIGHT_CORAL
            elif search_map[idx]["searched"]:
                color = CORN_FLOWER_BLUE
            pygame.draw.rect(surface, color, (x, y, cell_size, cell_size))
            if idx != 0 and not cell_map[idx].left["connection"]:
                pygame.draw.line(surface, BLACK, (x, y), (x, y + cell_size), 1)
            if not cell_map[idx].right["connection"]:
                pygame.draw.line(
                    surface,
                    BLACK,
                    (x + cell_size, y),
                    (x + cell_size, y + cell_size),
                    1,
                )
            if not cell_map[idx].top["connection"]:
                pygame.draw.line(surface, BLACK, (x, y), (x + cell_size, y), 1)
            if idx != (rows * cols - 1) and not cell_map[idx].bottom["connection"]:
                pygame.draw.line(
                    surface,
                    BLACK,
                    (x, y + cell_size),
                    (x + cell_size, y + cell_size),
                    1,
                )


def draw_scrollbar(surface, content_height, visible_height, scroll_y):
    if content_height <= visible_height:
        return
    scrollbar_width = 10
    scrollbar_x = surface.get_width() - scrollbar_width - 5
    pygame.draw.rect(
        surface,
        (200, 200, 200),
        (scrollbar_x, 0, scrollbar_width, visible_height),
        border_radius=5,
    )
    thumb_height = max(30, (visible_height / content_height) * visible_height)
    thumb_pos = (scroll_y / (content_height - visible_height)) * (
        visible_height - thumb_height
    )
    pygame.draw.rect(
        surface,
        (150, 150, 150),
        (scrollbar_x, thumb_pos, scrollbar_width, thumb_height),
        border_radius=5,
    )


def draw_button(surface, rect, text, font, is_hovered):
    color = BUTTON_HOVER if is_hovered else WHITE
    pygame.draw.rect(surface, color, rect, border_radius=5)
    pygame.draw.rect(surface, (180, 180, 180), rect, width=1, border_radius=5)
    txt_surf = font.render(text, True, BLACK)
    surface.blit(
        txt_surf,
        (
            rect.x + (rect.width - txt_surf.get_width()) // 2,
            rect.y + (rect.height - txt_surf.get_height()) // 2,
        ),
    )
