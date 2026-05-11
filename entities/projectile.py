# entities/projectile.py

import math

import pygame

from utils.sprite import load_image


class Projectile:
    def __init__(self, x, y, vx, vy, damage):
        self.x = x
        self.y = y
        self.vel_x = vx
        self.vel_y = vy
        self.damage = damage
        self.alive = True

        # Load arrow image (optional)
        self.original_image = load_image("assets/images/arrow.png", (20, 5))
        self.image = self.original_image
        self.rect = pygame.Rect(x, y, 20, 5)

        # Calculate rotation angle from velocity
        if self.original_image:
            angle = math.degrees(
                math.atan2(-self.vel_y, self.vel_x)
            )  # negate y because Pygame y is flipped
            self.image = pygame.transform.rotate(self.original_image, angle)
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.rect = pygame.Rect(x, y, 20, 5)

    def update(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        if self.image and self.original_image:
            self.rect.center = (int(self.x), int(self.y))
        else:
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

        # Remove if off screen (with generous margin)
        if (
            self.rect.right < -50
            or self.rect.left > 850
            or self.rect.bottom < -50
            or self.rect.top > 650
        ):
            self.alive = False

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, (200, 200, 50), self.rect)
