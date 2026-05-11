# utils/sound.py
import os
import sys

import pygame


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def load_sound(path):
    """Load a sound file, return None if not found or mixer not available."""
    if not pygame.mixer.get_init():
        print("Warning: Mixer not initialised – cannot load sound.")
        return None
    full_path = resource_path(path)
    if os.path.exists(full_path):
        return pygame.mixer.Sound(full_path)
    else:
        print(f"Warning: Sound file not found – {full_path}")
        return None
