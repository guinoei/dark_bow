# states/menu.py

import pygame

from settings import WHITE
from states import State
from ui.button import Button


class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.Font(None, 74)
        self.start_btn = Button(300, 250, 200, 50, "Start Game")
        self.controls_btn = Button(300, 320, 200, 50, "Controls")

    def handle_events(self, events):
        for event in events:
            if self.start_btn.handle_event(event):
                from states.playing import PlayingState

                self.game.change_state(PlayingState(self.game))
            if self.controls_btn.handle_event(event):
                from states.controls import ControlsState

                self.game.change_state(ControlsState(self.game))

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((20, 20, 20))

        title_surf = self.title_font.render("DARK BOW", True, WHITE)
        title_rect = title_surf.get_rect(center=(400, 100))
        screen.blit(title_surf, title_rect)

        self.start_btn.draw(screen)
        self.controls_btn.draw(screen)
