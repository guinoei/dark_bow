class State:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        """Process pygame events. `events` is the list from pygame.event.get()."""
        pass

    def update(self, dt):
        """Update logic. `dt` is delta time in milliseconds."""
        pass

    def draw(self, screen):
        """Draw to the screen surface."""
        pass

    def on_exit(self):
        """Called when the state is being replaced."""
        pass
