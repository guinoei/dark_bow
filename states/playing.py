# states/playing.py

import random

import pygame

from entities.boss import Boss
from entities.enemy import Enemy
from entities.player import Player
from settings import (
    BG_BOSS,
    BG_WAVE,
    BOSS_HP,
    GREEN,
    GROUND_Y,
    MUSIC_BOSS,
    MUSIC_WAVE,
    PLAYER_MAX_HP,
    RED,
    SOUND_HIT,
    SOUND_PLAYER_HURT,
    WHITE,
)
from states import State
from utils.sound import load_sound
from utils.sprite import load_image


class PlayingState(State):
    def __init__(self, game):
        super().__init__(game)
        self.player = Player(100, GROUND_Y - 50)
        self.enemies = []
        self.projectiles = []
        self.font = pygame.font.Font(None, 30)
        self.boss = None
        self.wave_cleared = False

        # Spawn control
        self.spawn_timer = 0
        self.spawn_interval = 1500
        self.total_enemies_to_spawn = 15
        self.spawned_count = 0

        # Sounds
        self.hit_sound = load_sound(SOUND_HIT)
        self.player_hurt_sound = load_sound(SOUND_PLAYER_HURT)

        # Backgrounds
        self.bg_wave = load_image(BG_WAVE, (800, 600))
        self.bg_boss = load_image(BG_BOSS, (800, 600))
        self.current_bg = self.bg_wave  # start with wave background

        # Music
        self.current_music = None
        self.play_music(MUSIC_WAVE)

    def play_music(self, path, loops=-1):
        """Safe music loading and playing."""
        if not pygame.mixer.get_init():
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loops)
            self.current_music = path
        except pygame.error as e:
            print(f"Could not play music {path}: {e}")

    def handle_events(self, events):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        new_arrow = self.player.handle_input(keys, events, current_time)
        if new_arrow:
            self.projectiles.append(new_arrow)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from states.menu import MenuState

                self.game.change_state(MenuState(self.game))

    def update(self, dt):
        dt_sec = dt / 1000.0
        current_time = pygame.time.get_ticks()

        # Player update
        self.player.update(dt_sec)

        # Spawn enemies
        if not self.wave_cleared and self.spawned_count < self.total_enemies_to_spawn:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_timer = 0
                self.spawn_enemy()
                self.spawned_count += 1

        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt_sec, self.player.rect, current_time)

        # Update boss if alive
        if self.boss and self.boss.alive:
            self.boss.update(dt_sec, self.player.rect, current_time)

        # Projectiles
        for proj in self.projectiles:
            proj.update(dt_sec)

        # Arrow vs enemy
        for proj in self.projectiles[:]:
            if not proj.alive:
                continue
            for enemy in self.enemies[:]:
                if proj.rect.colliderect(enemy.rect):
                    dead = enemy.take_damage(proj.damage)
                    proj.alive = False
                    if self.hit_sound:
                        self.hit_sound.play()
                    if dead:
                        self.enemies.remove(enemy)
                    break
        self.projectiles = [p for p in self.projectiles if p.alive]

        # Arrow vs boss
        if self.boss and self.boss.alive:
            for proj in self.projectiles[:]:
                if proj.rect.colliderect(self.boss.rect):
                    self.boss.take_damage(proj.damage)
                    proj.alive = False
                    if self.hit_sound:
                        self.hit_sound.play()
            self.projectiles = [p for p in self.projectiles if p.alive]

        # Enemy melee vs player
        for enemy in self.enemies:
            hitbox = enemy.get_attack_hitbox()
            if (
                hitbox
                and hitbox.colliderect(self.player.rect)
                and not self.player.invincible
            ):
                self.player.take_damage(enemy.attack_damage)
                if self.player_hurt_sound:
                    self.player_hurt_sound.play()
                if self.player.rect.centerx < enemy.rect.centerx:
                    self.player.rect.x -= 30
                else:
                    self.player.rect.x += 30

        # Boss attacks vs player
        if self.boss and self.boss.alive:
            # Charge
            if (
                self.boss.rect.colliderect(self.player.rect)
                and not self.player.invincible
            ):
                self.player.take_damage(20)
                if self.player_hurt_sound:
                    self.player_hurt_sound.play()
                if self.player.rect.centerx < self.boss.rect.centerx:
                    self.player.rect.x -= 50
                else:
                    self.player.rect.x += 50
            # Shockwaves
            for proj in self.boss.projectiles:
                if (
                    proj.rect.colliderect(self.player.rect)
                    and not self.player.invincible
                ):
                    self.player.take_damage(proj.damage)
                    if self.player_hurt_sound:
                        self.player_hurt_sound.play()
                    proj.alive = False

        # Enemy separation
        for _ in range(3):
            for i, e1 in enumerate(self.enemies):
                for e2 in self.enemies[i + 1 :]:
                    if e1.rect.colliderect(e2.rect):
                        dx = e1.rect.centerx - e2.rect.centerx
                        if dx == 0:
                            dx = 1
                        overlap = (e1.rect.width + e2.rect.width) / 2 - abs(dx)
                        if overlap > 0:
                            shift = overlap / 2
                            direction = 1 if dx > 0 else -1
                            e1.rect.x += shift * direction
                            e2.rect.x -= shift * direction

        # Spawn boss when wave cleared
        if (
            not self.wave_cleared
            and len(self.enemies) == 0
            and self.spawned_count >= self.total_enemies_to_spawn
        ):
            self.wave_cleared = True
            self.boss = Boss(400, GROUND_Y - 90)
            # Switch to boss background and music
            self.current_bg = self.bg_boss if self.bg_boss else self.bg_wave
            self.play_music(MUSIC_BOSS)

        # Player death
        if self.player.hp <= 0:
            from states.game_over import GameOverState

            self.game.change_state(GameOverState(self.game))

        # Boss death
        if self.boss and not self.boss.alive:
            from states.victory import VictoryState

            self.game.change_state(VictoryState(self.game))

    def spawn_enemy(self):
        for _ in range(30):
            x = random.randint(50, 750)
            y = GROUND_Y - 45
            temp_rect = pygame.Rect(x, y, 35, 45)
            if temp_rect.colliderect(self.player.rect.inflate(40, 40)):
                continue
            overlaps = False
            for enemy in self.enemies:
                if temp_rect.colliderect(enemy.rect.inflate(20, 20)):
                    overlaps = True
                    break
            if not overlaps:
                self.enemies.append(Enemy(x, y))
                return
        self.enemies.append(Enemy(random.randint(50, 750), GROUND_Y - 45))

    def draw(self, screen):
        # Background
        if self.current_bg:
            screen.blit(self.current_bg, (0, 0))
        else:
            screen.fill((30, 30, 40))

        # Ground
        pygame.draw.rect(screen, (80, 50, 30), (0, GROUND_Y, 800, 600 - GROUND_Y))

        # Projectiles
        for proj in self.projectiles:
            proj.draw(screen)

        # Enemies
        for enemy in self.enemies:
            enemy.draw(screen)

        # Boss
        if self.boss and self.boss.alive:
            self.boss.draw(screen)
            # Boss health bar
            bar_width = 400
            bar_height = 20
            bar_x = (800 - bar_width) // 2
            bar_y = 50
            pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            health_width = int(bar_width * (self.boss.hp / self.boss.max_hp))
            pygame.draw.rect(
                screen, (200, 0, 0), (bar_x, bar_y, health_width, bar_height)
            )
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
            boss_text = self.font.render("PELUCEVIL", True, WHITE)
            screen.blit(
                boss_text,
                (bar_x + bar_width // 2 - boss_text.get_width() // 2, bar_y - 25),
            )

        # Player
        self.player.draw(screen)

        # Player health bar
        bar_x, bar_y = 10, 10
        bar_width = 200
        bar_height = 20
        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        health_width = int(bar_width * (self.player.hp / self.player.max_hp))
        health_color = GREEN if self.player.hp > 30 else RED
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        hp_text = self.font.render(
            f"HP: {self.player.hp}/{self.player.max_hp}", True, WHITE
        )
        screen.blit(hp_text, (bar_x, bar_y + 25))

        # Enemy count (during wave)
        if not self.wave_cleared:
            remaining = (
                self.total_enemies_to_spawn - self.spawned_count + len(self.enemies)
            )
            count_text = self.font.render(
                f"Enemies: {remaining}/{self.total_enemies_to_spawn}", True, WHITE
            )
            screen.blit(count_text, (620, 10))

    def on_exit(self):
        """Stop music when leaving the playing state."""
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
