# states/victory.py

import pygame

from settings import BLACK, SOUND_VICTORY, WHITE, YELLOW
from states import State
from utils.sound import load_sound


class VictoryState(State):
    def __init__(self, game):
        super().__init__(game)
        self.font_large = pygame.font.Font(None, 80)
        self.font_small = pygame.font.Font(None, 30)
        self.alpha = 0
        self.fade_in = True
        self.victory_sound = load_sound(SOUND_VICTORY)
        if self.victory_sound:
            self.victory_sound.play()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                from states.menu import MenuState

                self.game.change_state(MenuState(self.game))

    def update(self, dt):
        if self.fade_in:
            self.alpha += dt * 0.3
            if self.alpha >= 255:
                self.alpha = 255
                self.fade_in = False

    def draw(self, screen):
        screen.fill(BLACK)

        text_surf = self.font_large.render("VICTORY ACHIEVED", True, YELLOW)
        text_surf.set_alpha(min(255, self.alpha))
        text_rect = text_surf.get_rect(center=(400, 250))
        screen.blit(text_surf, text_rect)

        prompt_surf = self.font_small.render("ESPAÇO para voltar ao MENU", True, WHITE)
        prompt_surf.set_alpha(min(255, self.alpha))
        prompt_rect = prompt_surf.get_rect(center=(400, 350))
        screen.blit(prompt_surf, prompt_rect)
