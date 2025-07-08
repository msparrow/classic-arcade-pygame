"""
Pygame implementation of the classic arcade game Galaga.
"""

import pygame
import sys
import random
import math

from config import BLACK, WHITE, RED, GREEN, BLUE, YELLOW
from utils import draw_text, pause_menu, settings_menu, Particle, create_explosion
import scores

# --- Initialization ---
pygame.init()

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

PLAYER_SIZE = 40
PLAYER_SPEED = 5
PLAYER_BULLET_SPEED = 10
PLAYER_MAX_BULLETS = 2

ENEMY_SIZE = 40
ENEMY_BULLET_SPEED = 7

# --- Game State Enums ---
class EnemyState:
    ENTERING = 1
    FORMATION = 2
    DIVING = 3
    REFORMING = 4
    TRACTOR_BEAM = 5
    CHALLENGE_FLIGHT = 6

class EnemyType:
    DRONE = 1
    BOSS = 2

# --- Helper Functions ---
def create_starfield(num_stars):
    """Creates a list of stars for the background."""
    return [{'x': random.randint(0, SCREEN_WIDTH), 'y': random.randint(0, SCREEN_HEIGHT), 'speed': random.uniform(0.5, 2)} for _ in range(num_stars)]

def draw_starfield(screen, stars):
    """Draws and updates the starfield."""
    for star in stars:
        star['y'] += star['speed']
        if star['y'] > SCREEN_HEIGHT:
            star['y'] = 0
            star['x'] = random.randint(0, SCREEN_WIDTH)
        pygame.draw.circle(screen, (150, 150, 150), (int(star['x']), int(star['y'])), 1)

# --- Classes ---
class Player:
    def __init__(self):
        self.respawn()
        self.lives = 3
        self.dual_fighter = False
        self.is_captured = False
        self.score = 0
        self.captured_by = None

    def respawn(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - PLAYER_SIZE // 2, SCREEN_HEIGHT - 60, PLAYER_SIZE, PLAYER_SIZE)
        self.is_captured = False
        self.captured_by = None

    def move(self, dx):
        self.rect.x += dx
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def draw(self, screen):
        if self.is_captured:
            return

        if self.dual_fighter:
            self.draw_single_ship(screen, self.rect.centerx - PLAYER_SIZE, self.rect.y)
            self.draw_single_ship(screen, self.rect.centerx, self.rect.y)
        else:
            self.draw_single_ship(screen, self.rect.x, self.rect.y)

    def draw_single_ship(self, screen, x, y):
        body_rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        pygame.draw.polygon(screen, WHITE, [(body_rect.centerx, body_rect.top), (body_rect.left, body_rect.bottom), (body_rect.right, body_rect.bottom)])
        pygame.draw.rect(screen, RED, (body_rect.centerx - 5, body_rect.centery, 10, 15))

class CapturedFighter:
    def __init__(self, boss):
        self.boss = boss
        self.rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        self.state = 'CAPTURED'
        self.rescue_path = None
        self.rescue_step = 0

    def update(self, player_rect):
        if self.state == 'CAPTURED':
            self.rect.centerx = self.boss.rect.centerx
            self.rect.centery = self.boss.rect.top - 30
        elif self.state == 'RESCUED':
            if self.rescue_path and self.rescue_step < len(self.rescue_path):
                self.rect.center = self.rescue_path[self.rescue_step]
                self.rescue_step += 1
            else:
                self.boss = None

    def start_rescue(self, player_rect):
        self.state = 'RESCUED'
        start_pos = self.rect.center
        end_pos = (player_rect.centerx, player_rect.y)
        self.rescue_path = [ (start_pos[0] + (end_pos[0] - start_pos[0]) * t, start_pos[1] + (end_pos[1] - start_pos[1]) * t) for t in [i/30 for i in range(31)]]
        self.rescue_step = 0

    def draw(self, screen):
        Player.draw_single_ship(self, screen, self.rect.x, self.rect.y)

class Bullet:
    def __init__(self, x, y, speed, color):
        self.rect = pygame.Rect(x - 2, y, 4, 15)
        self.speed = speed
        self.color = color

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Enemy:
    def __init__(self, enemy_type, formation_pos=None):
        self.type = enemy_type
        self.state = EnemyState.ENTERING
        self.formation_pos = formation_pos
        self.rect = pygame.Rect(-100, -100, ENEMY_SIZE, ENEMY_SIZE)
        self.health = 2 if self.type == EnemyType.BOSS else 1
        self.path = None
        self.path_step = 0
        self.tractor_beam_active = False
        self.tractor_beam_timer = 0
        self.captured_ship = None

    def set_path(self, path):
        self.path = path
        self.path_step = 0
        if self.path:
            self.rect.center = self.path[0]

    def update(self, player_pos):
        if self.path and self.path_step < len(self.path):
            self.rect.center = self.path[self.path_step]
            self.path_step += 1
        else:
            if self.state == EnemyState.ENTERING:
                self.state = EnemyState.FORMATION
                self.rect.center = self.formation_pos
            elif self.state == EnemyState.DIVING or self.state == EnemyState.CHALLENGE_FLIGHT:
                self.state = EnemyState.REFORMING

        if self.state == EnemyState.FORMATION:
            self.rect.centerx = self.formation_pos[0] + math.sin(pygame.time.get_ticks() / 500) * 10
            self.rect.centery = self.formation_pos[1] + math.cos(pygame.time.get_ticks() / 500) * 5
        elif self.state == EnemyState.TRACTOR_BEAM:
            self.tractor_beam_timer -= 1
            if self.tractor_beam_timer <= 0:
                self.tractor_beam_active = False
                self.state = EnemyState.DIVING
                self.path = self.generate_bezier_curve(self.rect.center, self.rect.center, (random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 50), (random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 50), 100)
                self.path_step = 0
        elif self.state == EnemyState.REFORMING:
            target_x, target_y = self.formation_pos
            dx, dy = target_x - self.rect.centerx, target_y - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist < 5:
                self.state = EnemyState.FORMATION
            else:
                self.rect.x += (dx / dist) * 4
                self.rect.y += (dy / dist) * 4

    def start_dive(self, player_pos):
        if self.type == EnemyType.BOSS and random.random() < 0.3:
            self.state = EnemyState.TRACTOR_BEAM
            self.tractor_beam_active = True
            self.tractor_beam_timer = 180
            start_pos, end_pos = self.rect.center, (self.rect.centerx, SCREEN_HEIGHT / 2)
            self.path = self.generate_bezier_curve(start_pos, start_pos, end_pos, end_pos, 30)
        else:
            self.state = EnemyState.DIVING
            start_pos = self.rect.center
            control_1 = (random.randint(0, SCREEN_WIDTH), start_pos[1] + 100)
            control_2 = (player_pos[0] + random.randint(-100, 100), player_pos[1] - 100)
            end_pos = (random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 50)
            self.path = self.generate_bezier_curve(start_pos, control_1, control_2, end_pos, 100)
        self.path_step = 0

    def generate_bezier_curve(self, p0, p1, p2, p3, num_points):
        points = []
        for i in range(num_points):
            t = i / (num_points - 1) if num_points > 1 else 0
            x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
            y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
            points.append((x, y))
        return points

    def draw(self, screen):
        if self.type == EnemyType.BOSS:
            color = (255, 0, 255)
            if self.health == 1: color = (255, 128, 255)
            pygame.draw.polygon(screen, color, [(self.rect.left, self.rect.top), (self.rect.right, self.rect.top), (self.rect.centerx, self.rect.bottom)])
        else:
            color = (0, 255, 255)
            pygame.draw.polygon(screen, color, [(self.rect.centerx, self.rect.top), (self.rect.left, self.rect.bottom - 10), (self.rect.right, self.rect.bottom - 10)])
        if self.tractor_beam_active:
            self.draw_tractor_beam(screen)

    def draw_tractor_beam(self, screen):
        beam_width, beam_height = 100, SCREEN_HEIGHT - self.rect.bottom
        alpha = 100 + math.sin(pygame.time.get_ticks() * 0.02) * 50
        beam_surface = pygame.Surface((beam_width, beam_height), pygame.SRCALPHA)
        pygame.draw.polygon(beam_surface, (100, 200, 255, alpha), [(0,0), (beam_width, 0), (beam_width*0.75, beam_height), (beam_width*0.25, beam_height)])
        screen.blit(beam_surface, (self.rect.centerx - beam_width / 2, self.rect.bottom))

    def shoot(self, bullets):
        if self.state == EnemyState.DIVING and random.random() < 0.02:
            bullets.append(Bullet(self.rect.centerx, self.rect.bottom, ENEMY_BULLET_SPEED, YELLOW))

class Formation:
    def __init__(self):
        self.enemies = []
        self.formation_positions = self.create_formation_positions()

    def create_formation_positions(self):
        return [(150 + col * 50, 50 + row * 50) for row in range(5) for col in range(10)]

    def create_wave(self, wave_num):
        self.enemies = []
        num_drones, num_bosses = min(20 + wave_num * 2, 40), min(4 + wave_num, 10)
        enemy_specs = [(EnemyType.BOSS, pos) for pos in self.formation_positions[:num_bosses]] + [(EnemyType.DRONE, pos) for pos in self.formation_positions[num_bosses:num_bosses + num_drones]]
        random.shuffle(enemy_specs)
        for i, (enemy_type, pos) in enumerate(enemy_specs):
            enemy = Enemy(enemy_type, pos)
            self.enemies.append(enemy)
            self.assign_entry_path(enemy, i)

    def assign_entry_path(self, enemy, index):
        path_type = index % 4
        if path_type == 0:
            start_pos, end_pos = (-50, 100 + (index % 10) * 20), enemy.formation_pos
            control_1, control_2 = (SCREEN_WIDTH / 4, 50), (end_pos[0], 50)
        elif path_type == 1:
            start_pos, end_pos = (SCREEN_WIDTH + 50, 100 + (index % 10) * 20), enemy.formation_pos
            control_1, control_2 = (SCREEN_WIDTH * 3 / 4, 50), (end_pos[0], 50)
        else:
            start_pos, end_pos = (SCREEN_WIDTH / 2, -50), enemy.formation_pos
            control_1, control_2 = (50, 150) if path_type == 2 else (SCREEN_WIDTH - 50, 150), (end_pos[0] + (-100 if path_type == 2 else 100), end_pos[1] + 100)
        path = enemy.generate_bezier_curve(start_pos, control_1, control_2, end_pos, 120)
        enemy.set_path(path)

    def update(self, player_pos):
        if all(e.state == EnemyState.FORMATION for e in self.enemies) and random.random() < 0.01:
            dive_candidates = [e for e in self.enemies if e.state == EnemyState.FORMATION]
            if dive_candidates: random.choice(dive_candidates).start_dive(player_pos)
        for enemy in self.enemies: enemy.update(player_pos)

    def draw(self, screen):
        for enemy in self.enemies: enemy.draw(screen)

    def all_enemies_entered(self):
        return all(e.state != EnemyState.ENTERING for e in self.enemies)

def game_loop(screen, clock, font, level, player, captured_fighters):
    pygame.display.set_caption(f"Galaga - Level {level}")
    player_bullets, enemy_bullets, particles, stars = [], [], [], create_starfield(100)
    formation = Formation()
    formation.create_wave(level)
    wave_intro_timer, respawn_timer = pygame.time.get_ticks(), 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return player.score, 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not player.is_captured:
                    if len(player_bullets) < (PLAYER_MAX_BULLETS * (2 if player.dual_fighter else 1)):
                        bullets_to_fire = [player.rect.centerx] if not player.dual_fighter else [player.rect.centerx - PLAYER_SIZE, player.rect.centerx]
                        for x_pos in bullets_to_fire:
                            player_bullets.append(Bullet(x_pos, player.rect.top, -PLAYER_BULLET_SPEED, WHITE))
                if event.key == pygame.K_p:
                    if pause_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT) == 'quit': return player.score, 'quit'

        keys = pygame.key.get_pressed()
        if not player.is_captured:
            if keys[pygame.K_LEFT]: player.move(-PLAYER_SPEED)
            if keys[pygame.K_RIGHT]: player.move(PLAYER_SPEED)

        for group in [player_bullets, enemy_bullets, particles]:
            for item in group[:]:
                item.update()
                if hasattr(item, 'rect') and not screen.get_rect().colliderect(item.rect): group.remove(item)
                elif hasattr(item, 'life') and item.life <= 0: group.remove(item)

        formation.update(player.rect.center)
        for enemy in formation.enemies: enemy.shoot(enemy_bullets)
        for fighter in captured_fighters: fighter.update(player.rect)
        if any(f.state == 'RESCUED' and not f.boss for f in captured_fighters):
            player.dual_fighter = True
            captured_fighters[:] = [f for f in captured_fighters if f.state != 'RESCUED']

        for bullet in player_bullets[:]:
            for enemy in formation.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    if bullet in player_bullets: player_bullets.remove(bullet)
                    enemy.health -= 1
                    if enemy.health <= 0:
                        player.score += 400 if enemy.type == EnemyType.BOSS and enemy.state == EnemyState.DIVING else 200 if enemy.type == EnemyType.BOSS else 100
                        create_explosion(particles, enemy.rect.centerx, enemy.rect.centery, RED)
                        if enemy.captured_ship:
                            enemy.captured_ship.start_rescue(player.rect)
                            enemy.captured_ship = None
                        formation.enemies.remove(enemy)
                    break
            for fighter in captured_fighters[:]:
                if fighter.state == 'CAPTURED' and bullet.rect.colliderect(fighter.rect):
                     if bullet in player_bullets: player_bullets.remove(bullet)
                     create_explosion(particles, fighter.rect.centerx, fighter.rect.centery, RED)
                     captured_fighters.remove(fighter)

        if not player.is_captured:
            for bullet in enemy_bullets[:]:
                if bullet.rect.colliderect(player.rect):
                    enemy_bullets.remove(bullet)
                    player.lives -= 1
                    player.dual_fighter = False
                    create_explosion(particles, player.rect.centerx, player.rect.centery, GREEN)
                    if player.lives <= 0: return player.score, 'game_over'
                    player.is_captured, respawn_timer = True, pygame.time.get_ticks()
            for enemy in formation.enemies[:]:
                if enemy.state in [EnemyState.DIVING, EnemyState.TRACTOR_BEAM] and enemy.rect.colliderect(player.rect):
                    player.lives -= 1
                    player.dual_fighter = False
                    create_explosion(particles, player.rect.centerx, player.rect.centery, GREEN, 50)
                    formation.enemies.remove(enemy)
                    if player.lives <= 0: return player.score, 'game_over'
                    player.is_captured, respawn_timer = True, pygame.time.get_ticks()
                if enemy.tractor_beam_active and pygame.Rect(enemy.rect.centerx - 50, enemy.rect.bottom, 100, SCREEN_HEIGHT).colliderect(player.rect):
                    player.lives -= 1
                    player.dual_fighter = False
                    enemy.captured_ship = CapturedFighter(enemy)
                    captured_fighters.append(enemy.captured_ship)
                    enemy.tractor_beam_active = False
                    if player.lives <= 0: return player.score, 'game_over'
                    player.is_captured, respawn_timer = True, pygame.time.get_ticks()
                    break

        if player.is_captured and pygame.time.get_ticks() - respawn_timer > 2000:
            player.respawn()

        screen.fill(BLACK)
        draw_starfield(screen, stars)
        player.draw(screen)
        for group in [player_bullets, enemy_bullets, formation.enemies, captured_fighters, particles]:
            for item in group: item.draw(screen)

        draw_text(f"Score: {player.score}", font, WHITE, screen, 100, 20)
        draw_text(f"Level: {level}", font, WHITE, screen, SCREEN_WIDTH / 2, 20)
        for i in range(player.lives):
            ship_rect = pygame.Rect(SCREEN_WIDTH - 40 - (i * (PLAYER_SIZE + 5)), 10, PLAYER_SIZE, PLAYER_SIZE)
            pygame.draw.polygon(screen, WHITE, [(ship_rect.centerx, ship_rect.top), (ship_rect.left, ship_rect.bottom), (ship_rect.right, ship_rect.bottom)])

        if pygame.time.get_ticks() - wave_intro_timer < 2000:
            draw_text(f"STAGE {level}", font, BLUE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        elif not formation.all_enemies_entered():
             draw_text("GET READY!", font, YELLOW, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        if not formation.enemies and formation.all_enemies_entered():
            return player.score, 'next_level'

        pygame.display.flip()
        clock.tick(60)

def challenging_stage(screen, clock, font, level, player):
    pygame.display.set_caption(f"Galaga - Challenging Stage {level // 4}")
    stars, player_bullets, particles, enemies = create_starfield(100), [], [], []
    start_time = pygame.time.get_ticks()
    total_enemies = 40
    enemies_spawned = 0
    last_spawn_time = 0

    # Pre-defined paths for the challenging stage
    paths = [
        # Path 1: Swoop from left
        lambda i: Enemy(EnemyType.DRONE).set_path(Enemy(EnemyType.DRONE).generate_bezier_curve((-50, 100 + i*15), (SCREEN_WIDTH/2, 50), (SCREEN_WIDTH - 50, 200), (SCREEN_WIDTH + 50, 100 + i*15), 240)),
        # Path 2: Swoop from right
        lambda i: Enemy(EnemyType.DRONE).set_path(Enemy(EnemyType.DRONE).generate_bezier_curve((SCREEN_WIDTH + 50, 100 + i*15), (SCREEN_WIDTH/2, 50), (50, 200), (-50, 100 + i*15), 240)),
        # Path 3: Figure eight
        lambda i: Enemy(EnemyType.BOSS).set_path(Enemy(EnemyType.BOSS).generate_bezier_curve((SCREEN_WIDTH/2, -50), (100, 200), (700, 400), (SCREEN_WIDTH/2, SCREEN_HEIGHT+50), 300))
    ]

    while pygame.time.get_ticks() - start_time < 20000: # 20 second stage
        current_time = pygame.time.get_ticks()
        if enemies_spawned < total_enemies and current_time - last_spawn_time > 200:
            path_func = paths[enemies_spawned % len(paths)]
            enemy = path_func(enemies_spawned)
            if enemy:
                enemy.state = EnemyState.CHALLENGE_FLIGHT
                enemies.append(enemy)
                enemies_spawned += 1
                last_spawn_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return player.score, 'quit'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if len(player_bullets) < (PLAYER_MAX_BULLETS * (2 if player.dual_fighter else 1)):
                    bullets_to_fire = [player.rect.centerx] if not player.dual_fighter else [player.rect.centerx - PLAYER_SIZE, player.rect.centerx]
                    for x_pos in bullets_to_fire:
                        player_bullets.append(Bullet(x_pos, player.rect.top, -PLAYER_BULLET_SPEED, WHITE))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player.move(-PLAYER_SPEED)
        if keys[pygame.K_RIGHT]: player.move(PLAYER_SPEED)

        for group in [player_bullets, enemies, particles]:
            for item in group[:]:
                if hasattr(item, 'update'): item.update(player.rect.center)
                if hasattr(item, 'rect') and not screen.get_rect().colliderect(item.rect) and item in enemies: group.remove(item)
                elif hasattr(item, 'rect') and item.rect.bottom < 0 and item in player_bullets: group.remove(item)
                elif hasattr(item, 'life') and item.life <= 0: group.remove(item)

        for bullet in player_bullets[:]:
            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    if bullet in player_bullets: player_bullets.remove(bullet)
                    enemy.health -= 1
                    if enemy.health <= 0:
                        player.score += 500 # Higher score for challenge stage
                        create_explosion(particles, enemy.rect.centerx, enemy.rect.centery, BLUE)
                        enemies.remove(enemy)
                    break

        screen.fill(BLACK)
        draw_starfield(screen, stars)
        player.draw(screen)
        for group in [player_bullets, enemies, particles]:
            for item in group: item.draw(screen)

        draw_text("CHALLENGING STAGE", font, YELLOW, screen, SCREEN_WIDTH / 2, 40)
        draw_text(f"Enemies Destroyed: {total_enemies - len(enemies)}/{total_enemies}", font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 40)

        pygame.display.flip()
        clock.tick(60)

    if not enemies:
        player.score += 10000 # Perfect bonus
        draw_text("PERFECT! +10000", font, GREEN, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 2000)

    return player.score, 'next_level'

def main_menu(screen, clock, font, small_font):
    BACKGROUND_COLOR = (30, 10, 10)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (255, 0, 0)
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("Galaga", font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        mx, my = pygame.mouse.get_pos()
        button_width, button_height, button_spacing = 250, 60, 20
        settings_y = SCREEN_HEIGHT / 2 - 50
        start_y = settings_y + button_height + button_spacing
        quit_y = start_y + button_height + button_spacing
        buttons = [
            {"text": "Settings", "rect": pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, settings_y, button_width, button_height), "action": "settings"},
            {"text": "Start Game", "rect": pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, start_y, button_width, button_height), "action": "play"},
            {"text": "Back to Menu", "rect": pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, quit_y, button_width, button_height), "action": "quit"}
        ]
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        if button["action"] == "settings":
                            _, status = settings_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT, pygame.mixer.music.get_volume())
                            if status == 'quit': return 'quit'
                        else:
                            return button["action"]
        for button in buttons:
            current_button_color = BUTTON_HOVER_COLOR if button["rect"].collidepoint(mx, my) else BUTTON_COLOR
            pygame.draw.rect(screen, current_button_color, button["rect"], border_radius=10)
            pygame.draw.rect(screen, BORDER_COLOR, button["rect"], 2, border_radius=10)
            draw_text(button["text"], small_font, TEXT_COLOR, screen, button["rect"].centerx, button["rect"].centery)
        pygame.display.flip()
        clock.tick(15)

def end_screen(screen, clock, font, message):
    BACKGROUND_COLOR = (30, 10, 10)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (255, 0, 0)
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)
    title_font = pygame.font.Font(None, 60)
    button_font = pygame.font.Font(None, 40)
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text(message, title_font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
        mx, my = pygame.mouse.get_pos()
        button_width, button_height, button_spacing = 250, 60, 20
        play_again_y = SCREEN_HEIGHT / 2 + 20
        quit_y = play_again_y + button_height + button_spacing
        buttons = [
            {"text": "Play Again", "rect": pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, play_again_y, button_width, button_height), "action": "play_again"},
            {"text": "Back to Menu", "rect": pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, quit_y, button_width, button_height), "action": "quit"}
        ]
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos): return button["action"]
        for button in buttons:
            current_button_color = BUTTON_HOVER_COLOR if button["rect"].collidepoint(mx, my) else BUTTON_COLOR
            pygame.draw.rect(screen, current_button_color, button["rect"], border_radius=10)
            pygame.draw.rect(screen, BORDER_COLOR, button["rect"], 2, border_radius=10)
            draw_text(button["text"], button_font, TEXT_COLOR, screen, button["rect"].centerx, button["rect"].centery)
        pygame.display.flip()
        clock.tick(15)

def next_level_screen(screen, clock, font, level, score):
    BACKGROUND_COLOR = (10, 10, 30)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (0, 255, 255)
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)
    title_font = pygame.font.Font(None, 60)
    button_font = pygame.font.Font(None, 40)
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text(f"Level {level} Complete!", title_font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
        draw_text(f"Score: {score}", font, TEXT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        mx, my = pygame.mouse.get_pos()
        button_width, button_height, button_spacing = 250, 60, 20
        continue_y = SCREEN_HEIGHT / 2 + 100
        quit_y = continue_y + button_height + button_spacing
        buttons = [
            {"text": "Continue", "rect": pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, continue_y, button_width, button_height), "action": "continue"},
            {"text": "Back to Menu", "rect": pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, quit_y, button_width, button_height), "action": "quit"}
        ]
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos): return button["action"]
        for button in buttons:
            current_button_color = BUTTON_HOVER_COLOR if button["rect"].collidepoint(mx, my) else BUTTON_COLOR
            pygame.draw.rect(screen, current_button_color, button["rect"], border_radius=10)
            pygame.draw.rect(screen, BORDER_COLOR, button["rect"], 2, border_radius=10)
            draw_text(button["text"], button_font, TEXT_COLOR, screen, button["rect"].centerx, button["rect"].centery)
        pygame.display.flip()
        clock.tick(15)

def run_game(screen, clock):
    """Main function to manage the game states for Galaga."""
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)

    while True:
        menu_choice = main_menu(screen, clock, font, small_font)
        if menu_choice == 'quit':
            return

        player = Player()
        captured_fighters = []
        current_level = 1
        game_active = True

        while game_active:
            if current_level % 4 == 0:
                player.score, outcome = challenging_stage(screen, clock, small_font, current_level, player)
            else:
                player.score, outcome = game_loop(screen, clock, small_font, current_level, player, captured_fighters)

            if outcome == 'next_level':
                current_level += 1
                choice = next_level_screen(screen, clock, small_font, current_level - 1, player.score)
                if choice == 'quit':
                    game_active = False
            elif outcome == 'game_over':
                scores.save_score("Galaga", player.score)
                choice = end_screen(screen, clock, font, f"Game Over! Score: {player.score}")
                if choice == 'quit':
                    game_active = False
                elif choice == 'play_again':
                    player = Player()
                    captured_fighters = []
                    current_level = 1
            elif outcome == 'quit':
                game_active = False

if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()
