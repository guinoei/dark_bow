# ui/button.py

import pygame

from settings import BLACK, GREY, WHITE


class Button:
    def __init__(self, x, y, width, height, text, font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False

    def handle_event(self, event):
        """Returns True if the button is clicked. Also updates hover state."""
        if event.type == pygame.MOUSEMOTION:
            # Update hover state on every mouse movement
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Direct collision check on click – always works
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen):
        # Choose color based on hover
        colour = GREY if self.is_hovered else WHITE
        pygame.draw.rect(screen, colour, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # border

        # Render text
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
