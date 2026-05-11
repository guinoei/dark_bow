# entities/boss.py
import pygame

from entities.projectile import Projectile
from settings import (
    BOSS_HP,
    DARK_RED,
    GROUND_Y,
    SOUND_BOSS_DEATH,
    SOUND_BOSS_HURT,
    SOUND_BOSS_SLAM,
    WHITE,
)
from utils.sound import load_sound
from utils.sprite import load_image


class Boss:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 80, 90)
        self.hp = BOSS_HP
        self.max_hp = BOSS_HP
        self.alive = True
        self.vel_x = 0

        # State
        self.current_action = None
        self.action_timer = 0
        self.cooldown_timer = 1000  # idle after attack

        # Projectiles (shockwaves)
        self.projectiles = []

        # Charge attack
        self.charge_speed = 400
        self.charge_duration = 1.0  # seconds
        self.charge_damage = 20

        # Slam attack
        self.slam_damage = 25
        self.shockwave_speed = 300

        self.facing_right = True
        self.hurt_sound = load_sound(SOUND_BOSS_HURT)
        self.death_sound = load_sound(SOUND_BOSS_DEATH)
        self.slam_sound = load_sound(SOUND_BOSS_SLAM)
        self.rect = pygame.Rect(x, y, 80, 90)
        self.image = load_image("assets/images/boss.png", (80, 90))

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            if self.death_sound:
                self.death_sound.play()
        else:
            if self.hurt_sound:
                self.hurt_sound.play()

    def pick_action(self, player_x):
        """Choose attack based on distance."""
        # Always face player
        self.facing_right = self.rect.centerx < player_x

        dist = abs(self.rect.centerx - player_x)
        if dist > 150:
            self.start_charge()
        else:
            self.start_slam()

    def start_charge(self):
        self.current_action = "charge"
        self.action_timer = self.charge_duration
        # Dash direction towards player (facing_right already set)
        self.vel_x = self.charge_speed if self.facing_right else -self.charge_speed

    def start_slam(self):
        self.current_action = "slam"
        self.action_timer = 0.5  # wind-up time
        self.vel_x = 0

    def update(self, dt, player_rect, current_time):
        # dt in seconds
        if not self.alive:
            return

        # Decrement action timer
        if self.current_action:
            self.action_timer -= dt
            if self.action_timer <= 0:
                self.finish_action()

        # Update movement
        if self.current_action == "charge":
            self.rect.x += self.vel_x * dt
            # Stop at screen edges
            if self.rect.left < 0:
                self.rect.left = 0
                self.action_timer = 0  # end charge early
            if self.rect.right > 800:
                self.rect.right = 800
                self.action_timer = 0

        # Update boss's projectiles (shockwaves)
        for proj in self.projectiles:
            proj.update(dt)
        self.projectiles = [p for p in self.projectiles if p.alive]

        # Cooldown between attacks
        if not self.current_action:
            self.cooldown_timer -= dt * 1000  # convert to ms
            if self.cooldown_timer <= 0:
                self.pick_action(player_rect.centerx)
                self.cooldown_timer = 2000  # ms before next attack

        # Keep on ground
        self.rect.bottom = GROUND_Y

    def finish_action(self):
        """Called when action timer ends."""
        if self.current_action == "slam":
            # Spawn shockwave
            self.spawn_shockwave()
        # End action
        self.current_action = None
        self.vel_x = 0

    def spawn_shockwave(self):
        # Shockwave goes in the direction the boss is facing
        direction = 1 if self.facing_right else -1
        # Spawn at boss's feet
        x = self.rect.centerx
        y = self.rect.bottom - 10
        proj = Projectile(x, y, self.shockwave_speed * direction, 0, self.slam_damage)
        # Make it larger visually (optional)
        proj.rect.width = 30
        proj.rect.height = 10
        self.projectiles.append(proj)

    def draw(self, screen):
        if self.image:
            image_to_draw = self.image
            if not self.facing_right:
                image_to_draw = pygame.transform.flip(self.image, True, False)
            screen.blit(image_to_draw, self.rect)
        else:
            # Fallback: dark red rectangle + horns
            pygame.draw.rect(screen, DARK_RED, self.rect)
            # Eyes
            eye_y = self.rect.centery - 10
            if self.facing_right:
                pygame.draw.rect(screen, WHITE, (self.rect.right - 20, eye_y, 10, 10))
            else:
                pygame.draw.rect(screen, WHITE, (self.rect.left + 10, eye_y, 10, 10))
            # Horns
            horn_points_left = [
                (self.rect.left, self.rect.top),
                (self.rect.left + 15, self.rect.top - 20),
                (self.rect.left + 30, self.rect.top),
            ]
            horn_points_right = [
                (self.rect.right - 30, self.rect.top),
                (self.rect.right - 15, self.rect.top - 20),
                (self.rect.right, self.rect.top),
            ]
            pygame.draw.polygon(screen, (100, 0, 0), horn_points_left)
            pygame.draw.polygon(screen, (100, 0, 0), horn_points_right)

        # Draw boss projectiles (shockwaves) - can also be sprited later
        for proj in self.projectiles:
            proj.draw(screen)
