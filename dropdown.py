# dropdown.py
import pygame
from config import WHITE, BUTTON_HOVER, BLACK


class Dropdown:
    def __init__(
        self,
        x,
        y,
        w,
        h,
        font,
        options,
        selected_index=0,
        main_color=WHITE,
        hover_color=BUTTON_HOVER,
        text_color=BLACK,
        z_index=0,
    ):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.options = options
        self.selected_index = selected_index
        self.main_color = main_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.z_index = z_index  # Higher z_index means drawn on top
        self.expanded = False
        self.option_rects = []  # For collision detection

    def draw(self, surface, label, y_offset=0):
        adjusted_y = self.rect.y - y_offset
        # Draw label to the left
        label_surf = self.font.render(label, True, BLACK)
        label_x = self.rect.x - label_surf.get_width() - 10
        label_y = adjusted_y + (self.rect.height - label_surf.get_height()) // 2
        surface.blit(label_surf, (label_x, label_y))
        # Draw main rectangle
        current_color = self.hover_color if self.expanded else self.main_color
        adjusted_rect = pygame.Rect(
            self.rect.x, adjusted_y, self.rect.width, self.rect.height
        )
        pygame.draw.rect(surface, current_color, adjusted_rect, border_radius=4)
        # Draw selected text
        selected_text = self.options[self.selected_index]
        txt_surf = self.font.render(selected_text, True, self.text_color)
        surface.blit(
            txt_surf,
            (
                self.rect.x + 5,
                adjusted_y + (self.rect.height - txt_surf.get_height()) // 2,
            ),
        )
        # Draw arrow
        arrow_surf = self.font.render("▼", True, self.text_color)
        surface.blit(
            arrow_surf,
            (
                self.rect.right - arrow_surf.get_width() - 5,
                adjusted_y + (self.rect.height - arrow_surf.get_height()) // 2,
            ),
        )
        # Draw options if expanded
        self.option_rects = []
        if self.expanded:
            for i, option in enumerate(self.options):
                opt_rect = pygame.Rect(
                    self.rect.x,
                    adjusted_y + self.rect.height * (i + 1),
                    self.rect.width,
                    self.rect.height,
                )
                self.option_rects.append(opt_rect)
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if opt_rect.collidepoint(mouse_x, mouse_y):
                    pygame.draw.rect(surface, self.hover_color, opt_rect)
                else:
                    pygame.draw.rect(surface, self.main_color, opt_rect)
                opt_surf = self.font.render(option, True, self.text_color)
                surface.blit(
                    opt_surf,
                    (
                        opt_rect.x + 5,
                        opt_rect.y + (opt_rect.height - opt_surf.get_height()) // 2,
                    ),
                )

    def handle_event(self, event, y_offset=0):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            mouse_y += y_offset
            adjusted_rect = pygame.Rect(
                self.rect.x, self.rect.y - y_offset, self.rect.width, self.rect.height
            )
            if adjusted_rect.collidepoint(mouse_x, mouse_y - y_offset):
                self.expanded = not self.expanded
                return False
            elif self.expanded:
                for i, opt_rect in enumerate(self.option_rects):
                    if opt_rect.collidepoint(mouse_x, mouse_y):
                        self.selected_index = i
                        self.expanded = False
                        return True
                self.expanded = False
        return False
