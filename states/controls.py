import pygame

from settings import WHITE
from states import State


class ControlsState(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 50)
        self.return_font = pygame.font.Font(None, 24)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                from states.menu import MenuState

                self.game.change_state(MenuState(self.game))

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((20, 20, 20))

        title = self.title_font.render("CONTROLS", True, WHITE)
        screen.blit(title, title.get_rect(center=(400, 80)))

        lines = [
            "ESQUERDA: A",
            "DIREITA: D",
            "PULAR: W",
            "ATIRAR: BOTÃO DO MOUSE",
            "USE O MOUSE PARA MIRAR",
            "",
            "ESC: VOLTAR AO MENU",
        ]

        for i, line in enumerate(lines):
            text = self.font.render(line, True, WHITE)
            screen.blit(text, (200, 160 + i * 40))

        note = self.return_font.render(
            "pressione qualquer tecla", True, (150, 150, 150)
        )
        screen.blit(note, note.get_rect(center=(400, 550)))
