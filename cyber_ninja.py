"""
Pygame implementation of a side-scrolling action platformer: Cyber-Ninja Showdown.

This script contains the complete game logic for a platformer, including player and enemy mechanics,
- level design, collision detection, and a scrolling camera.
"""

import pygame
import sys
import random
import math
import os

# Background constants
NUM_STARS = 100
STAR_SPEED = 0.5

# Import shared modules and constants
from config import BLACK, WHITE, RED, GREEN, BLUE, YELLOW
from utils import draw_text, pause_menu, settings_menu
import scores

# --- Game Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 750
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAVITY = 0.64
PLAYER_JUMP = -6
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
        self.player = create_surface_from_data(PLAYER_SPRITE_DATA, scale=6)
        self.walking_bot = create_surface_from_data(WALKING_BOT_DATA, scale=12)
        self.turret = create_surface_from_data(TURRET_DATA, scale=12)
        self.platform_tile = create_surface_from_data(PLATFORM_TILE_DATA, scale=20) # Tiles are larger
        self.projectile = create_surface_from_data(PROJECTILE_DATA)
        self.enemy_projectile = create_surface_from_data(ENEMY_PROJECTILE_DATA, scale=3)

# --- Level Map ---


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
        self.score = 0
        self.facing_direction = vec(1, 0) # Initial facing direction

    def update(self, platforms, all_sprites, magic_particles):
        self.acc = vec(0, PLAYER_GRAVITY)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.acc.x = -PLAYER_ACC
            self.facing_direction.x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.acc.x = PLAYER_ACC
            self.facing_direction.x = 1

        # Check if player is on a platform
        self.rect.y += 1
        on_platform = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.y -= 1

        # Flying logic
        if not on_platform and keys[pygame.K_SPACE]:
            self.acc.y = -PLAYER_ACC * 0.2  # Reduced upward acceleration
            # Create magic particles
            particle = MagicParticle(self.rect.center, -self.vel.normalize() * 2)
            all_sprites.add(particle)
            magic_particles.add(particle)

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
        return self.facing_direction

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

class FlyingBot(Enemy):
    def __init__(self, pos):
        super().__init__(pos, assets.walking_bot)
        self.vel = vec(random.uniform(-1, 1), random.uniform(-1, 1))
        self.last_shot = pygame.time.get_ticks()
        self.direction_change_timer = pygame.time.get_ticks()

    def update(self, player, all_sprites, enemy_projectiles):
        now = pygame.time.get_ticks()
        if now - self.direction_change_timer > random.randint(1500, 3500):
            self.direction_change_timer = now
            self.vel = vec(random.uniform(-1, 1), random.uniform(-1, 1))

        self.pos += self.vel
        self.rect.center = self.pos

        dist_to_player = self.pos.distance_to(player.pos)
        if dist_to_player < 400:
            if now - self.last_shot > 1200:
                self.last_shot = now
                direction = (player.pos - self.pos).normalize()
                proj = EnemyProjectile(self.rect.center, direction, self)
                all_sprites.add(proj)
                enemy_projectiles.add(proj)

class WalkingBot(Enemy):
    def __init__(self, pos):
        super().__init__(pos, assets.turret)
        self.vel = vec(random.choice([-2, 2]), 0)
        self.last_shot = 0
        self.direction_timer = 0

    def update(self, platforms, player, all_sprites, enemy_projectiles):
        self.pos += self.vel
        self.rect.midbottom = self.pos

        self.rect.y += 1
        platform_hits = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.y -= 1
        
        now = pygame.time.get_ticks()
        if not platform_hits or now - self.direction_timer > 3000:
            self.vel.x *= -1
            self.direction_timer = now

        dist_to_player = self.pos.distance_to(player.pos)
        if dist_to_player < 300:
            if now - self.last_shot > 1500:
                self.last_shot = now
                direction = (player.pos - self.pos).normalize()
                proj = EnemyProjectile(self.rect.center, direction, self)
                all_sprites.add(proj)
                enemy_projectiles.add(proj)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction):
        super().__init__()
        self.image = assets.projectile
        self.rect = self.image.get_rect(center=pos)
        self.vel = direction * 10

    def update(self, camera_offset):
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y
        # Remove if it leaves the extended screen area (view + buffer)
        screen_rect_extended = pygame.Rect(
            camera_offset.x - 200, camera_offset.y - 200,
            SCREEN_WIDTH + 400, SCREEN_HEIGHT + 400
        )
        if not screen_rect_extended.colliderect(self.rect):
            self.kill()

class EnemyProjectile(Projectile):
    def __init__(self, pos, direction, owner):
        super().__init__(pos, direction)
        self.image = assets.enemy_projectile
        self.vel = direction * 7
        self.owner = owner

    def update(self, camera_offset):
        super().update(camera_offset)

class MagicParticle(pygame.sprite.Sprite):
    def __init__(self, pos, vel):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill((150, 50, 255)) # Purple
        self.rect = self.image.get_rect(center=pos)
        self.vel = vel
        self.lifetime = random.randint(20, 40)

    def update(self, camera_offset):
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

# --- Main Game Functions ---
class WorldManager:
    def __init__(self, all_sprites, platforms, enemies, player_start_pos):
        self.all_sprites = all_sprites
        self.platforms = platforms
        self.enemies = enemies

        self.chunk_size = 15 * assets.platform_tile.get_width()
        self.generated_chunks = set() # Now stores (chunk_x, chunk_y)
        self.last_platform_end_x = 0

        # Generate the initial starting area
        self.generate_initial_chunks(player_start_pos)

    def generate_initial_chunks(self, player_start_pos):
        start_chunk_x = int(player_start_pos[0] // self.chunk_size)
        start_chunk_y = int(player_start_pos[1] // self.chunk_size)

        # Create a smaller, solid starting platform
        initial_platform_tiles = 20
        start_x = player_start_pos[0] - (initial_platform_tiles // 2) * assets.platform_tile.get_width()

        for i in range(initial_platform_tiles):
            x = start_x + i * assets.platform_tile.get_width()
            p = Platform(x, player_start_pos[1])
            self.all_sprites.add(p)
            self.platforms.add(p)
        
        self.last_platform_end_x = start_x + initial_platform_tiles * assets.platform_tile.get_width()

        # Mark the initial chunk as generated
        self.generated_chunks.add((start_chunk_x, start_chunk_y))

    def manage(self, player_pos):
        player_chunk_x = int(player_pos.x // self.chunk_size)
        player_chunk_y = int(player_pos.y // self.chunk_size)

        # Generate new chunks around the player (horizontally and vertically)
        for y in range(player_chunk_y - 1, player_chunk_y + 3):
            for x in range(player_chunk_x - 2, player_chunk_x + 3):
                if (x, y) not in self.generated_chunks:
                    self.generate_chunk(x, y)

        # Despawn chunks far from the player
        chunks_to_remove = []
        for (chunk_x, chunk_y) in self.generated_chunks:
            if abs(chunk_x - player_chunk_x) > 3 or abs(chunk_y - player_chunk_y) > 3:
                chunks_to_remove.append((chunk_x, chunk_y))
        
        for chunk in chunks_to_remove:
            self.despawn_chunk(chunk)

    def generate_chunk(self, chunk_x, chunk_y):
        self.generated_chunks.add((chunk_x, chunk_y))
        chunk_start_x = chunk_x * self.chunk_size
        chunk_start_y = chunk_y * self.chunk_size

        # Ensure there's always a platform below
        if not self.is_chunk_generated(chunk_x, chunk_y + 1):
            platform_count = random.randint(1, 3)
        else:
            platform_count = random.randint(0, 2)

        for _ in range(platform_count):
            platform_length = random.randint(5, 12)
            platform_x = chunk_start_x + random.randint(0, self.chunk_size - platform_length * assets.platform_tile.get_width())
            platform_y = chunk_start_y + random.randint(0, self.chunk_size - assets.platform_tile.get_height())

            for i in range(platform_length):
                x = platform_x + i * assets.platform_tile.get_width()
                p = Platform(x, platform_y)
                self.all_sprites.add(p)
                self.platforms.add(p)

                if random.random() < 0.3:
                    if random.random() < 0.5:
                        bot = WalkingBot((x, platform_y))
                        self.all_sprites.add(bot)
                        self.enemies.add(bot)
                    else:
                        flying_bot = FlyingBot((x, platform_y - 100))
                        self.all_sprites.add(flying_bot)
                        self.enemies.add(flying_bot)

    def is_chunk_generated(self, chunk_x, chunk_y):
        return (chunk_x, chunk_y) in self.generated_chunks

    def despawn_chunk(self, chunk):
        chunk_x, chunk_y = chunk
        chunk_start_x = chunk_x * self.chunk_size
        chunk_end_x = chunk_start_x + self.chunk_size
        chunk_start_y = chunk_y * self.chunk_size
        chunk_end_y = chunk_start_y + self.chunk_size

        for sprite in list(self.all_sprites):
            if chunk_start_x <= sprite.rect.x < chunk_end_x and \
               chunk_start_y <= sprite.rect.y < chunk_end_y:
                sprite.kill()
        
        if chunk in self.generated_chunks:
            self.generated_chunks.remove(chunk)


def run_game(screen, clock):
    """Main function to manage the game states for Cyber-Ninja Showdown."""
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    enemy_projectiles = pygame.sprite.Group()
    magic_particles = pygame.sprite.Group()

    # Background stars
    stars = []
    for _ in range(NUM_STARS):
        star_x = random.randint(0, SCREEN_WIDTH)
        star_y = random.randint(0, SCREEN_HEIGHT)
        star_size = random.randint(1, 3)
        stars.append([star_x, star_y, star_size])

    # Setup player and world
    player_start_pos = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 150)
    player = Player(player_start_pos)
    all_sprites.add(player)

    world_manager = WorldManager(all_sprites, platforms, enemies, player_start_pos)

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
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    player.is_flying = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                player.shoot(all_sprites, projectiles)

        # Update
        player.update(platforms, all_sprites, magic_particles)
        projectiles.update(camera_offset)
        enemy_projectiles.update(camera_offset)
        magic_particles.update(camera_offset)
        for enemy in enemies:
            if isinstance(enemy, WalkingBot):
                enemy.update(platforms, player, all_sprites, enemy_projectiles)
            elif isinstance(enemy, FlyingBot):
                enemy.update(player, all_sprites, enemy_projectiles)
        
        # Update world
        world_manager.manage(player.pos)

        # Update camera
        camera_offset.x += (player.rect.centerx - camera_offset.x - SCREEN_WIDTH / 2) * 0.15
        camera_offset.y += (player.rect.centery - camera_offset.y - SCREEN_HEIGHT / 2) * 0.15


        # --- Collision Detection ---
        # Projectiles hitting enemies
        hits = pygame.sprite.groupcollide(enemies, projectiles, False, True)
        for enemy, proj_list in hits.items():
            for _ in proj_list:
                enemy.take_damage(25)
                player.score += 10
                player.health = min(player.health + 10, PLAYER_HEALTH)

        # Enemy projectiles hitting player
        hits = pygame.sprite.spritecollide(player, enemy_projectiles, True)
        for hit in hits:
            if isinstance(hit.owner, FlyingBot):
                player.health -= 1
            else:
                player.health -= 20
            if player.health <= 0:
                running = False

        # Player colliding with enemies
        hits = pygame.sprite.spritecollide(player, enemies, False)
        if hits:
            # No damage from overlapping enemies directly
            if player.health <= 0:
                running = False # Game Over

        # --- Drawing ---
        screen.fill((30, 30, 50)) # Dark blue background

        # Draw stars
        for star in stars:
            star[0] -= STAR_SPEED # Scroll stars
            if star[0] < 0:
                star[0] = SCREEN_WIDTH
                star[1] = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(screen, WHITE, (int(star[0]), int(star[1])), star[2])

        for sprite in all_sprites:
            screen.blit(sprite.image, sprite.rect.topleft - camera_offset)

        # Draw HUD
        draw_text(f"Health: {player.health}", pygame.font.Font(None, 36), WHITE, screen, 100, 30)
        draw_text(f"Score: {player.score}", pygame.font.Font(None, 36), WHITE, screen, 100, 60)

        # Performance Metrics
        fps = clock.get_fps()
        draw_text(f"FPS: {fps:.2f}", pygame.font.Font(None, 24), WHITE, screen, SCREEN_WIDTH - 150, 20)

        pygame.display.flip()
        clock.tick(120)

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
