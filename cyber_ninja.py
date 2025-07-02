"""
Pygame implementation of a side-scrolling action platformer: Cyber-Ninja Showdown.

This script contains the complete game logic for a platformer, including player and enemy mechanics,
- level design, collision detection, and a scrolling camera.
"""

import pygame
import sys
import random
import math

# Import shared modules and constants
from config import BLACK, WHITE, RED, GREEN, BLUE, YELLOW
from utils import draw_text, pause_menu, settings_menu
import scores

# --- Game Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAVITY = 0.8
PLAYER_JUMP = -18
PLAYER_HEALTH = 100
ENEMY_HEALTH = 50

# --- Asset Creation ---
# Helper function to create surfaces from pixel art data
def create_surface_from_data(data, scale=4):
    """Creates a Pygame Surface from a 2D list of color keys."""
    width = len(data[0])
    height = len(data)
    
    # Define the color palette
    palette = {
        '.': (0, 0, 0, 0),      # Transparent
        'B': (0, 0, 0),        # Black
        'W': (255, 255, 255),  # White
        'R': (200, 0, 0),      # Red
        'r': (255, 100, 100),  # Light Red
        'G': (0, 150, 0),      # Green
        'g': (100, 255, 100),  # Light Green
        'S': (150, 150, 150),  # Gray (Shadow)
        'M': (200, 200, 200),  # Metal Gray
        'Y': (255, 255, 0),    # Yellow
        'C': (0, 200, 200),    # Cyan
        'N': (100, 50, 0),     # Brown (Ninja Rope)
        'H': (255, 200, 150)   # Skin/Highlight
    }
    
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for y, row in enumerate(data):
        for x, color_key in enumerate(row):
            color = palette.get(color_key)
            if color:
                surface.set_at((x, y), color)
    
    # Scale up the surface to make it visible
    return pygame.transform.scale(surface, (width * scale, height * scale))

# --- Pixel Art Data ---
PLAYER_SPRITE_DATA = [
    "....B...",
    "...BBB..",
    "..BSB...",
    ".B.B.B..",
    ".BMBMB..",
    ".B.R.B..",
    "..N.N...",
    ".B...B..",
]

WALKING_BOT_DATA = [
    ".RRR.",
    "R.R.R",
    "R.Y.R",
    ".R.R.",
    ".B.B.",
]

TURRET_DATA = [
    "..M..",
    ".MMM.",
    "MRMRM",
    "BBBBB",
]

PLATFORM_TILE_DATA = [
    "MMMM",
    "MS.M",
    "M..M",
    "MMMM",
]

PROJECTILE_DATA = [
    ".Y.",
    "YCY",
    ".Y.",
]

ENEMY_PROJECTILE_DATA = [
    "R",
    "r",
]

# --- Game Sprites ---
# Using a simple class to hold the created surfaces
class Assets:
    def __init__(self):
        self.player = create_surface_from_data(PLAYER_SPRITE_DATA)
        self.walking_bot = create_surface_from_data(WALKING_BOT_DATA)
        self.turret = create_surface_from_data(TURRET_DATA)
        self.platform_tile = create_surface_from_data(PLATFORM_TILE_DATA, scale=20) # Tiles are larger
        self.projectile = create_surface_from_data(PROJECTILE_DATA)
        self.enemy_projectile = create_surface_from_data(ENEMY_PROJECTILE_DATA, scale=3)

# --- Level Map ---
LEVEL_MAP = [
    "                                ",
    "                                ",
    "                                ",
    "                                ",
    "                                ",
    " P                              ",
    "XXXXXXXXXXXXXXXXX     XXXXXXXXXX",
    "                                ",
    "                                ",
    "    T                         T ",
    "XXXXXXXXX    XXXXXXXX    XXXXXXX",
    "                                ",
    "                                ",
    "      W                         ",
    "XXXXXXXXXXXXX      W      XXXXXX",
    "                                ",
    "                                ",
    "   XXXXXXXXXX    XXXXXXXXXXXX   ",
    "                                ",
    "                                ",
    "T          W                  T ",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
]

# --- Classes ---
vec = pygame.math.Vector2

class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos):
        super().__init__()
        self.image = assets.player
        self.rect = self.image.get_rect(midbottom=start_pos)
        self.pos = vec(start_pos)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.health = PLAYER_HEALTH
        self.last_shot = 0

    def update(self, platforms):
        self.acc = vec(0, PLAYER_GRAVITY)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.acc.x = -PLAYER_ACC
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.acc.x = PLAYER_ACC

        # Apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # Equations of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # Collision detection
        self.rect.midbottom = self.pos
        self.collide_with_platforms(platforms)

    def jump(self, platforms):
        # Jump only if standing on a platform
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.y -= 1
        if hits:
            self.vel.y = PLAYER_JUMP

    def shoot(self, all_sprites, projectiles):
        # No cooldown for unlimited shurikens
        projectile = Projectile(self.rect.center, self.get_direction())
        all_sprites.add(projectile)
        projectiles.add(projectile)

    def get_direction(self):
        # Simple direction check for shooting
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            return vec(-1, 0)
        return vec(1, 0)

    def collide_with_platforms(self, platforms):
        self.rect.midbottom = self.pos
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            # Find the highest platform we are colliding with
            main_platform = max(hits, key=lambda h: h.rect.bottom)
            if self.vel.y > 0: # Moving down
                if self.pos.y > main_platform.rect.top:
                    self.pos.y = main_platform.rect.top + 1
                    self.vel.y = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = assets.platform_tile
        self.rect = self.image.get_rect(topleft=(x, y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midbottom=pos)
        self.pos = vec(pos)
        self.health = ENEMY_HEALTH

    def take_damage(self, amount):
        # Disappear on first hit
        self.kill()

class WalkingBot(Enemy):
    def __init__(self, pos):
        super().__init__(pos, assets.walking_bot)
        self.vel = vec(random.choice([-2, 2]), 0)
        self.last_shot = 0

    def update(self, platforms, player, all_sprites, enemy_projectiles):
        self.pos += self.vel
        self.rect.midbottom = self.pos
        # Simple patrol: reverse direction at edges or walls
        self.rect.y += 1
        platform_hits = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.y -= 1
        if not platform_hits:
            self.vel.x *= -1

        # Shooting logic
        dist_to_player = self.pos.distance_to(player.pos)
        if dist_to_player < 250:
            # Check if facing the player
            is_facing_player = (player.pos.x > self.pos.x and self.vel.x > 0) or \
                               (player.pos.x < self.pos.x and self.vel.x < 0)
            if is_facing_player:
                now = pygame.time.get_ticks()
                if now - self.last_shot > 2000: # Cooldown
                    self.last_shot = now
                    direction = (player.pos - self.pos).normalize()
                    proj = EnemyProjectile(self.rect.center, direction)
                    all_sprites.add(proj)
                    enemy_projectiles.add(proj)

class Turret(Enemy):
    def __init__(self, pos):
        super().__init__(pos, assets.turret)
        self.last_shot = 0

    def update(self, player, all_sprites, enemy_projectiles):
        # Fire at player if within range
        dist = self.pos.distance_to(player.pos)
        if dist < 300:
            now = pygame.time.get_ticks()
            if now - self.last_shot > 1500: # Cooldown
                self.last_shot = now
                direction = (player.pos - self.pos).normalize()
                proj = EnemyProjectile(self.rect.center, direction)
                all_sprites.add(proj)
                enemy_projectiles.add(proj)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction):
        super().__init__()
        self.image = assets.projectile
        self.rect = self.image.get_rect(center=pos)
        self.vel = direction * 10

    def update(self):
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y
        # Remove if it leaves the screen
        if not pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).colliderect(self.rect):
            self.kill()

class EnemyProjectile(Projectile):
    def __init__(self, pos, direction):
        super().__init__(pos, direction)
        self.image = assets.enemy_projectile
        self.vel = direction * 7

# --- Main Game Functions ---
def run_game(screen, clock):
    """Main function to manage the game states for Cyber-Ninja Showdown."""
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    enemy_projectiles = pygame.sprite.Group()

    # Build the level
    player_start_pos = (0, 0)
    for y, row in enumerate(LEVEL_MAP):
        for x, tile in enumerate(row):
            if tile == 'X':
                p = Platform(x * assets.platform_tile.get_width(), y * assets.platform_tile.get_height())
                all_sprites.add(p)
                platforms.add(p)
            elif tile == 'P':
                player_start_pos = (x * assets.platform_tile.get_width(), y * assets.platform_tile.get_height())
            elif tile == 'W':
                bot = WalkingBot((x * assets.platform_tile.get_width(), y * assets.platform_tile.get_height()))
                all_sprites.add(bot)
                enemies.add(bot)
            elif tile == 'T':
                turret = Turret((x * assets.platform_tile.get_width(), y * assets.platform_tile.get_height()))
                all_sprites.add(turret)
                enemies.add(turret)

    player = Player(player_start_pos)
    all_sprites.add(player)

    # Camera offset
    camera_offset = vec(0, 0)

    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump(platforms)
                if event.key == pygame.K_p:
                    pause_choice = pause_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT)
                    if pause_choice == 'quit':
                        running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                player.shoot(all_sprites, projectiles)

        # Update
        player.update(platforms)
        projectiles.update()
        enemy_projectiles.update()
        for enemy in enemies:
            if isinstance(enemy, WalkingBot):
                enemy.update(platforms, player, all_sprites, enemy_projectiles)
            elif isinstance(enemy, Turret):
                enemy.update(player, all_sprites, enemy_projectiles)
        
        # Update camera
        camera_offset.x += (player.rect.centerx - camera_offset.x - SCREEN_WIDTH / 2) * 0.05
        camera_offset.y += (player.rect.centery - camera_offset.y - SCREEN_HEIGHT / 2) * 0.05
        # Clamp camera to level boundaries
        camera_offset.x = max(0, min(camera_offset.x, len(LEVEL_MAP[0]) * assets.platform_tile.get_width() - SCREEN_WIDTH))
        camera_offset.y = max(0, min(camera_offset.y, len(LEVEL_MAP) * assets.platform_tile.get_height() - SCREEN_HEIGHT))


        # --- Collision Detection ---
        # Projectiles hitting enemies
        hits = pygame.sprite.groupcollide(enemies, projectiles, False, True)
        for enemy, proj_list in hits.items():
            for _ in proj_list:
                enemy.take_damage(25)

        # Enemy projectiles hitting player
        hits = pygame.sprite.spritecollide(player, enemy_projectiles, True)
        if hits:
            player.health -= 20
            if player.health <= 0:
                running = False # Game Over

        # Player colliding with enemies
        hits = pygame.sprite.spritecollide(player, enemies, False)
        if hits:
            player.health -= 1
            if player.health <= 0:
                running = False # Game Over

        # --- Drawing ---
        screen.fill((30, 30, 50)) # Dark blue background
        for sprite in all_sprites:
            screen.blit(sprite.image, sprite.rect.topleft - camera_offset)

        # Draw HUD
        draw_text(f"Health: {player.health}", pygame.font.Font(None, 36), WHITE, screen, 100, 30)
        if not enemies:
            draw_text("YOU WIN!", pygame.font.Font(None, 100), GREEN, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False

        pygame.display.flip()
        clock.tick(60)

    # Save score if the player won
    if not enemies:
        scores.save_score("Cyber-Ninja Showdown", 1000) # Placeholder score
    return 0

def get_instructions():
    """Returns a list of instructions for the game."""
    return [
        "A/D or Left/Right Arrows: Move",
        "Spacebar: Jump",
        "Left Mouse Click: Shoot Shuriken",
        "Defeat all enemies to win!",
    ]

# --- Initialization ---
# This is done globally once, so it's safe to have here.
assets = Assets()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Cyber-Ninja Showdown")
    clock = pygame.time.Clock()
    # A simple loop to show the placeholder screen
    run_game(screen, clock)
    pygame.quit()
    sys.exit()
