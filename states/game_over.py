# states/game_over.py

import pygame

from settings import BLACK, RED, SOUND_DEATH, WHITE
from states import State
from utils.sound import load_sound


class GameOverState(State):
    def __init__(self, game):
        super().__init__(game)
        self.font_large = pygame.font.Font(None, 90)
        self.font_small = pygame.font.Font(None, 30)
        self.alpha = 0
        self.fade_in = True
        self.death_sound = load_sound(SOUND_DEATH)
        if self.death_sound:
            self.death_sound.play()

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
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        text_surf = self.font_large.render("YOU DIED", True, RED)
        text_surf.set_alpha(min(255, self.alpha))
        text_rect = text_surf.get_rect(center=(400, 250))
        screen.blit(text_surf, text_rect)

        prompt_surf = self.font_small.render("ESPAÇO para voltar ao MENU", True, WHITE)
        prompt_surf.set_alpha(min(255, self.alpha))
        prompt_rect = prompt_surf.get_rect(center=(400, 350))
        screen.blit(prompt_surf, prompt_rect)
