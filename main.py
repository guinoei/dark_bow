import sys

import pygame

from settings import BLACK, FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from states.menu import MenuState


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("DARK BOW - Demo")
        self.clock = pygame.time.Clock()
        self.running = True

        # Start with the menu
        self.state = MenuState(self)

    def change_state(self, new_state):
        if self.state:
            self.state.on_exit()
        self.state = new_state

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)  # returns milliseconds since last frame

            # Event handling
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.state.handle_events(events)
            self.state.update(dt)

            # Drawing
            self.screen.fill(BLACK)
            self.state.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
