# entities/enemy.py

import pygame

from settings import RED, SOUND_ENEMY_DEATH, SOUND_ENEMY_HURT, WHITE
from utils.sound import load_sound
from utils.sprite import load_image

# Enemy state machine
IDLE = "idle"
CHASE = "chase"
ATTACK = "attack"


class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 35, 45)  # width, height
        self.vel_x = 0
        self.hp = 30
        self.max_hp = 30
        self.state = IDLE
        self.facing_right = True

        # Movement
        self.speed = 120  # pixels per second
        self.detection_range = (
            300  # px – start chasing if player within this x distance
        )

        # Attack
        self.attack_range = 40  # px – melee hit distance
        self.attack_damage = 10
        self.attack_cooldown = 1000  # ms between attacks
        self.last_attack_time = 0
        self.attack_active = False  # True for a short time to apply damage once
        self.attack_duration = 300  # ms (how long the hitbox is active)
        self.attack_timer = 0

        # Health bar above head
        self.font = pygame.font.Font(None, 16)
        self.hurt_sound = load_sound(SOUND_ENEMY_HURT)
        self.death_sound = load_sound(SOUND_ENEMY_DEATH)
        self.rect = pygame.Rect(x, y, 35, 45)
        self.image = load_image("assets/images/enemy.png", (35, 45))

    def update(self, dt, player_rect, current_time):
        """dt in seconds, player_rect is the player's rect, current_time in ms"""
        # State transitions
        dist = abs(self.rect.centerx - player_rect.centerx)

        if self.state == ATTACK:
            # Attack duration timer
            self.attack_timer -= dt * 1000  # convert to ms
            if self.attack_timer <= 0:
                self.state = IDLE
                self.attack_active = False
        else:
            if dist <= self.attack_range:
                self.state = ATTACK
                self.attack_timer = self.attack_duration
                self.attack_active = True
                self.last_attack_time = current_time
            elif dist <= self.detection_range:
                self.state = CHASE
            else:
                self.state = IDLE

        # Movement
        if self.state == CHASE:
            if self.rect.centerx < player_rect.centerx:
                self.vel_x = self.speed
                self.facing_right = True
            else:
                self.vel_x = -self.speed
                self.facing_right = False
        else:
            self.vel_x = 0

        # Apply movement
        self.rect.x += self.vel_x * dt

        # Keep on ground (no jumps for this enemy)
        from settings import GROUND_Y

        self.rect.bottom = min(self.rect.bottom, GROUND_Y)

        # Don't go off screen
        self.rect.clamp_ip(pygame.Rect(0, 0, 800, GROUND_Y + 100))

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            if self.death_sound:
                self.death_sound.play()
            return True  # dead
        else:
            if self.hurt_sound:
                self.hurt_sound.play()
            return False

    def get_attack_hitbox(self):
        """Returns a rect representing the melee strike area, or None if not active."""
        if not self.attack_active:
            return None
        # Small hitbox in front of the enemy
        hit_width = 20
        hit_height = self.rect.height
        if self.facing_right:
            hit_rect = pygame.Rect(
                self.rect.right, self.rect.top, hit_width, hit_height
            )
        else:
            hit_rect = pygame.Rect(
                self.rect.left - hit_width, self.rect.top, hit_width, hit_height
            )
        return hit_rect

    def draw(self, screen):
        if self.image:
            image_to_draw = self.image
            if not self.facing_right:
                image_to_draw = pygame.transform.flip(self.image, True, False)
            screen.blit(image_to_draw, self.rect)
        else:
            # Fallback: red rectangle
            pygame.draw.rect(screen, RED, self.rect)
            # Eyes
            eye_y = self.rect.centery - 5
            if self.facing_right:
                pygame.draw.rect(screen, WHITE, (self.rect.right - 10, eye_y, 6, 6))
            else:
                pygame.draw.rect(screen, WHITE, (self.rect.left + 4, eye_y, 6, 6))

        # Attack hitbox (debug visual)
        if self.attack_active:
            hit_rect = self.get_attack_hitbox()
            if hit_rect:
                pygame.draw.rect(screen, (255, 255, 0), hit_rect, 1)

        # Health bar (keep)
        bar_width = self.rect.width
        bar_height = 4
        bar_x = self.rect.x
        bar_y = self.rect.top - 8
        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * (self.hp / self.max_hp))
        pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, fill_width, bar_height))
