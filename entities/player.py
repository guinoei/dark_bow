# entities/player.py

import math

import pygame

from settings import (
    ARROW_DAMAGE,
    ARROW_SPEED,
    BLUE,
    GRAVITY,
    GROUND_Y,
    JUMP_STRENGTH,
    PLAYER_HEIGHT,
    PLAYER_MAX_HP,
    PLAYER_SPEED,
    PLAYER_WIDTH,
    SHOOT_COOLDOWN,
    YELLOW,
)
from utils.sprite import load_image


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

        # Aiming
        self.aim_angle = 0
        self.facing_right = True

        # Images
        self.original_image = load_image(
            "assets/images/player.png", (PLAYER_WIDTH, PLAYER_HEIGHT)
        )
        self.bow_image = load_image(
            "assets/images/bow.png"
        )  # <-- loaded as is, no scale

        # Combat
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 1000

        # Shooting
        self.last_shot_time = 0
        self.shoot_cooldown = SHOOT_COOLDOWN

        # Sound
        from settings import SOUND_SHOOT
        from utils.sound import load_sound

        self.shoot_sound = load_sound(SOUND_SHOOT)

    def handle_input(self, keys, events, current_time):
        # ----- Movement (unchanged) -----
        move_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        move_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]

        self.vel_x = 0
        if move_left:
            self.vel_x = -PLAYER_SPEED
        if move_right:
            self.vel_x = PLAYER_SPEED

        # Jump
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_w, pygame.K_UP, pygame.K_SPACE):
                    if self.on_ground:
                        self.vel_y = JUMP_STRENGTH
                        self.on_ground = False

        # ----- Aiming (mouse) -----
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.rect.centerx
        dy = mouse_y - self.rect.centery
        # Use atan2: angle from positive x-axis; note Pygame y points down
        self.aim_angle = math.atan2(-dy, dx)  # negate dy because math y points up

        # Facing direction based on mouse x
        self.facing_right = mouse_x >= self.rect.centerx

        # ----- Shooting -----
        shoot_pressed = pygame.mouse.get_pressed()[0]
        if shoot_pressed and current_time - self.last_shot_time >= self.shoot_cooldown:
            self.last_shot_time = current_time
            return self.shoot()
        return None

    def shoot(self):
        if self.shoot_sound:
            self.shoot_sound.play()

        # Calculate velocity vector
        vx = math.cos(self.aim_angle) * ARROW_SPEED
        vy = -math.sin(self.aim_angle) * ARROW_SPEED  # negate because screen y is down

        # Bullet spawn point at player center
        from entities.projectile import Projectile

        return Projectile(self.rect.centerx, self.rect.centery, vx, vy, ARROW_DAMAGE)

    def take_damage(self, amount):
        if self.invincible:
            return False
        self.hp -= amount
        self.invincible = True
        self.invincible_timer = self.invincible_duration
        return self.hp <= 0

    def update(self, dt):
        # Gravity & movement (unchanged)
        self.vel_y += GRAVITY * dt
        self.rect.x += self.vel_x * dt
        self.rect.y += self.vel_y * dt

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 800:
            self.rect.right = 800

        # Invincibility timer
        if self.invincible:
            self.invincible_timer -= dt * 1000
            if self.invincible_timer <= 0:
                self.invincible = False

    def draw(self, screen):
        # Invincibility flash
        if self.invincible and (pygame.time.get_ticks() // 100) % 2 == 0:
            return

        # Draw player body
        if self.original_image:
            body_to_draw = self.original_image
            if not self.facing_right:
                body_to_draw = pygame.transform.flip(self.original_image, True, False)
            screen.blit(body_to_draw, self.rect)
        else:
            pygame.draw.rect(screen, BLUE, self.rect)

        # Draw bow
        if self.bow_image:
            # Bow pivot point: slightly in front of the player's body
            offset = 15  # pixels from center
            hand_x = self.rect.centerx + (offset if self.facing_right else -offset)
            hand_y = self.rect.centery

            # Rotate bow according to aim angle
            angle = -math.degrees(self.aim_angle)  # negate for Pygame rotation
            rotated_bow = pygame.transform.rotate(self.bow_image, angle)

            # Place bow so its center is at the hand position
            # (This assumes the bow image's centre is the grip point)
            bow_rect = rotated_bow.get_rect(center=(hand_x, hand_y))

            # If player faces left, we need to mirror the bow horizontally
            # because the image is drawn for right-facing originally
            if not self.facing_right:
                rotated_bow = pygame.transform.flip(rotated_bow, True, False)

            screen.blit(rotated_bow, bow_rect)
        else:
            # Fallback: yellow aiming line
            bow_length = 25
            start_x, start_y = self.rect.centerx, self.rect.centery
            end_x = start_x + math.cos(self.aim_angle) * bow_length
            end_y = start_y - math.sin(self.aim_angle) * bow_length
            pygame.draw.line(screen, YELLOW, (start_x, start_y), (end_x, end_y), 3)
