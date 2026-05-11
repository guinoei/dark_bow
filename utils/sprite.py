# utils/sprite.py
import os
import sys

import pygame


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def load_image(path, scale_to=None):
    """Load an image from the assets folder, using resource_path."""
    full_path = resource_path(path)
    if os.path.exists(full_path):
        image = pygame.image.load(full_path).convert_alpha()
        if scale_to:
            image = pygame.transform.scale(image, scale_to)
        return image
    else:
        print(f"Warning: Image not found – {full_path}")
        return None
