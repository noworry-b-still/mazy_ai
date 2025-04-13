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
        dropdown_direction="down",  # New parameter: "down" or "up"
    ):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.options = options
        self.selected_index = selected_index
        self.main_color = main_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.z_index = z_index
        self.expanded = False
        self.option_rects = []  # For collision detection
        self.dropdown_direction = dropdown_direction

    def draw(self, surface, label, y_offset=0):
        adjusted_y = self.rect.y - y_offset

        # Draw label to the left
        label_surf = self.font.render(label, True, BLACK)
        label_x = self.rect.x - label_surf.get_width() - 10
        label_y = adjusted_y + (self.rect.height - label_surf.get_height()) // 2
        surface.blit(label_surf, (label_x, label_y))

        # Draw main dropdown box
        current_color = self.hover_color if self.expanded else self.main_color
        adjusted_rect = pygame.Rect(
            self.rect.x, adjusted_y, self.rect.width, self.rect.height
        )
        pygame.draw.rect(surface, current_color, adjusted_rect, border_radius=4)
        pygame.draw.rect(
            surface, (180, 180, 180), adjusted_rect, width=1, border_radius=4
        )

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

        # Draw arrow - different direction based on dropdown_direction
        arrow_char = "▼" if self.dropdown_direction == "down" else "▲"
        arrow_surf = self.font.render(arrow_char, True, self.text_color)
        surface.blit(
            arrow_surf,
            (
                self.rect.right - arrow_surf.get_width() - 5,
                adjusted_y + (self.rect.height - arrow_surf.get_height()) // 2,
            ),
        )

        # Draw options if expanded
        if self.expanded:
            # Calculate overlay position and dimensions based on dropdown direction
            overlay_height = len(self.options) * self.rect.height

            if self.dropdown_direction == "down":
                overlay_y = adjusted_y + self.rect.height
            else:  # "up"
                overlay_y = adjusted_y - overlay_height

            # Draw overlay to prevent UI conflicts
            overlay_rect = pygame.Rect(
                self.rect.x - 2, overlay_y, self.rect.width + 4, overlay_height + 2
            )
            pygame.draw.rect(surface, (220, 220, 220), overlay_rect, border_radius=4)
            pygame.draw.rect(
                surface, (180, 180, 180), overlay_rect, width=1, border_radius=4
            )

            # Create a clipping rect to ensure dropdown stays within surface
            clip_rect = surface.get_clip()

            # Create a different clipping rect based on dropdown direction
            if self.dropdown_direction == "down":
                dropdown_clip = pygame.Rect(
                    self.rect.x,
                    adjusted_y + self.rect.height,
                    self.rect.width,
                    min(
                        overlay_height,
                        surface.get_height() - (adjusted_y + self.rect.height),
                    ),
                )
            else:  # "up"
                dropdown_height = min(overlay_height, adjusted_y)
                dropdown_clip = pygame.Rect(
                    self.rect.x,
                    max(0, adjusted_y - overlay_height),
                    self.rect.width,
                    dropdown_height,
                )

            dropdown_clip = dropdown_clip.clip(clip_rect)
            surface.set_clip(dropdown_clip)

            # Draw each option
            self.option_rects = []
            for i, option in enumerate(self.options):
                if self.dropdown_direction == "down":
                    opt_y = adjusted_y + self.rect.height * (i + 1)
                else:  # "up"
                    opt_y = adjusted_y - self.rect.height * (i + 1)

                opt_rect = pygame.Rect(
                    self.rect.x,
                    opt_y,
                    self.rect.width,
                    self.rect.height,
                )
                self.option_rects.append(opt_rect)

                # Check if mouse is hovering over this option
                mouse_x, mouse_y = pygame.mouse.get_pos()
                is_hovered = opt_rect.collidepoint(mouse_x, mouse_y)

                # Draw option background
                if i == self.selected_index:
                    # Highlight the currently selected option
                    pygame.draw.rect(
                        surface, (230, 230, 250), opt_rect, border_radius=3
                    )
                elif is_hovered:
                    pygame.draw.rect(
                        surface, self.hover_color, opt_rect, border_radius=3
                    )
                else:
                    pygame.draw.rect(
                        surface, self.main_color, opt_rect, border_radius=3
                    )

                # Draw thin border around the option
                pygame.draw.rect(
                    surface, (200, 200, 200), opt_rect, width=1, border_radius=3
                )

                # Draw option text
                opt_surf = self.font.render(option, True, self.text_color)
                surface.blit(
                    opt_surf,
                    (
                        opt_rect.x + 5,
                        opt_rect.y + (opt_rect.height - opt_surf.get_height()) // 2,
                    ),
                )

            # Reset clipping
            surface.set_clip(clip_rect)

    def handle_event(self, event, y_offset=0):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            # Check if main dropdown rectangle is clicked
            adjusted_rect = pygame.Rect(
                self.rect.x, self.rect.y - y_offset, self.rect.width, self.rect.height
            )

            if adjusted_rect.collidepoint(mouse_x, mouse_y):
                self.expanded = not self.expanded
                return False

            # Check if any option is clicked (only if dropdown is expanded)
            elif self.expanded:
                for i, opt_rect in enumerate(self.option_rects):
                    if opt_rect.collidepoint(mouse_x, mouse_y):
                        old_index = self.selected_index
                        self.selected_index = i
                        self.expanded = False
                        return old_index != i  # Return True only if selection changed

                # If clicked outside the dropdown and its options, close it
                self.expanded = False

        # If we reach here, no dropdown option was changed
        return False
