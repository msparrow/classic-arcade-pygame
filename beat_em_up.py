"""
Pygame implementation of a 2D fighting game: Beat 'em Up.
"""

import pygame
import sys
import random

from config import BLACK, WHITE, RED, GREEN, BLUE, YELLOW
from utils import draw_text

# --- Game Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.75

# --- Fighter Constants ---
FIGHTER_WIDTH, FIGHTER_HEIGHT = 50, 120
FIGHTER_SPEED = 8
JUMP_POWER = -20
PUNCH_DAMAGE, KICK_DAMAGE = 10, 15
PUNCH_REACH, KICK_REACH = 60, 80
PUNCH_SPRITE_WIDTH = FIGHTER_WIDTH + 30
KICK_SPRITE_WIDTH = FIGHTER_WIDTH + 40


# --- Asset Creation ---
def create_fighter_surface(color1, color2):
    """Creates a simple pixel art fighter surface."""
    surface = pygame.Surface((FIGHTER_WIDTH, FIGHTER_HEIGHT), pygame.SRCALPHA)
    # Head
    pygame.draw.rect(surface, color2, (15, 0, 20, 20))
    # Body
    pygame.draw.rect(surface, color1, (10, 20, 30, 50))
    # Legs
    pygame.draw.rect(surface, color2, (10, 70, 10, 50))
    pygame.draw.rect(surface, color2, (30, 70, 10, 50))
    return surface

def create_punching_surface(color1, color2):
    """Creates a surface of the fighter punching."""
    surface = pygame.Surface((PUNCH_SPRITE_WIDTH, FIGHTER_HEIGHT), pygame.SRCALPHA)
    # Head
    pygame.draw.rect(surface, color2, (15, 0, 20, 20))
    # Body
    pygame.draw.rect(surface, color1, (10, 20, 30, 50))
    # Legs
    pygame.draw.rect(surface, color2, (10, 70, 10, 50))
    pygame.draw.rect(surface, color2, (30, 70, 10, 50))
    # Punching Arm
    pygame.draw.rect(surface, color1, (40, 30, 30, 15))
    return surface

def create_kicking_surface(color1, color2):
    """Creates a surface of the fighter kicking."""
    surface = pygame.Surface((KICK_SPRITE_WIDTH, FIGHTER_HEIGHT), pygame.SRCALPHA)
     # Head
    pygame.draw.rect(surface, color2, (15, 0, 20, 20))
    # Body
    pygame.draw.rect(surface, color1, (10, 20, 30, 50))
    # Standing Leg
    pygame.draw.rect(surface, color2, (10, 70, 10, 50))
    # Kicking Leg
    pygame.draw.rect(surface, color2, (20, 70, 50, 20))
    return surface

def create_snowy_mountain_bg():
    """Creates a snowy mountain background surface."""
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    # Sky
    surface.fill((100, 150, 255))
    # Distant mountains
    pygame.draw.polygon(surface, (180, 180, 200), [(0, 400), (150, 200), (300, 450), (500, 250), (650, 400), (800, 300), (800, 600), (0, 600)])
    # Closer mountains
    pygame.draw.polygon(surface, (220, 220, 240), [(0, 500), (250, 300), (450, 550), (600, 350), (800, 500), (800, 600), (0, 600)])
    # Snowy ground
    pygame.draw.rect(surface, (240, 240, 255), (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
    return surface

class Assets:
    def __init__(self):
        # Player 1 (Red)
        p1_color1, p1_color2 = (200, 0, 0), (150, 0, 0)
        self.fighter1 = create_fighter_surface(p1_color1, p1_color2)
        self.fighter1_punch = create_punching_surface(p1_color1, p1_color2)
        self.fighter1_kick = create_kicking_surface(p1_color1, p1_color2)

        # Player 2 (Blue)
        p2_color1, p2_color2 = (0, 0, 200), (0, 0, 150)
        self.fighter2 = create_fighter_surface(p2_color1, p2_color2)
        self.fighter2_punch = create_punching_surface(p2_color1, p2_color2)
        self.fighter2_kick = create_kicking_surface(p2_color1, p2_color2)
        
        self.background = create_snowy_mountain_bg()

assets = Assets()

# --- Fighter Class ---
class Fighter:
    def __init__(self, x, y, images, controls, facing_left):
        self.rect = pygame.Rect(x, y, FIGHTER_WIDTH, FIGHTER_HEIGHT)
        self.vel_y = 0
        self.health = 100
        self.images = images
        self.controls = controls
        self.facing_left = facing_left
        self.is_jumping = False
        self.is_attacking = False
        self.attack_type = None
        self.attack_cooldown = 0
        self.attack_frame_timer = 0
        self.hit = False

    def move(self, target):
        dx, dy = 0, 0
        keys = pygame.key.get_pressed()

        # Can only perform actions if not in an attack animation
        if not self.is_attacking:
            # Movement
            if keys[self.controls['left']]:
                dx = -FIGHTER_SPEED
            if keys[self.controls['right']]:
                dx = FIGHTER_SPEED
            # Jump
            if keys[self.controls['jump']] and not self.is_jumping:
                self.vel_y = JUMP_POWER
                self.is_jumping = True
            # Attacks (can only start an attack if cooldown is over)
            if self.attack_cooldown == 0:
                if keys[self.controls['punch']]:
                    self.attack(target, 'punch')
                if keys[self.controls['kick']]:
                    self.attack(target, 'kick')

        # Cooldowns are always running
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if self.attack_frame_timer > 0:
            self.attack_frame_timer -= 1
        else:
            self.is_attacking = False

        # Apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # Screen bounds
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right

        # Update position
        self.rect.x += dx
        self.rect.y += dy

        # Floor collision
        if self.rect.bottom > SCREEN_HEIGHT - 50:
            self.rect.bottom = SCREEN_HEIGHT - 50
            self.is_jumping = False

        # Face the opponent (don't turn mid-attack)
        if not self.is_attacking:
            if target.rect.centerx > self.rect.centerx:
                self.facing_left = False
            else:
                self.facing_left = True

    def attack(self, target, attack_type):
        self.is_attacking = True
        self.attack_frame_timer = 10  # Animation lasts for 10 frames
        self.attack_cooldown = 30     # Cannot attack again for 30 frames
        self.attack_type = attack_type
        
        reach = PUNCH_REACH if attack_type == 'punch' else KICK_REACH
        damage = PUNCH_DAMAGE if attack_type == 'punch' else KICK_DAMAGE
        
        attack_rect_x = self.rect.centerx - reach if self.facing_left else self.rect.centerx
        attack_rect = pygame.Rect(attack_rect_x, self.rect.y, reach, self.rect.height / 2)

        if attack_rect.colliderect(target.rect):
            target.health -= damage
            target.hit = True

    def draw(self, surface):
        current_image = self.images['idle']
        extra_width = 0
        if self.is_attacking:
            if self.attack_type == 'punch':
                current_image = self.images['punch']
                extra_width = PUNCH_SPRITE_WIDTH - FIGHTER_WIDTH
            elif self.attack_type == 'kick':
                current_image = self.images['kick']
                extra_width = KICK_SPRITE_WIDTH - FIGHTER_WIDTH

        img = pygame.transform.flip(current_image, self.facing_left, False)
        
        blit_pos = self.rect.topleft
        if self.is_attacking and self.facing_left:
            blit_pos = (self.rect.left - extra_width, self.rect.top)
            
        surface.blit(img, blit_pos)

# --- Main Game Functions ---
def run_game(screen, clock):
    """Main function to manage the game states for Beat 'em Up."""
    fighter1_images = {
        'idle': assets.fighter1,
        'punch': assets.fighter1_punch,
        'kick': assets.fighter1_kick
    }
    fighter1 = Fighter(200, 300, fighter1_images, {
        'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w,
        'punch': pygame.K_f, 'kick': pygame.K_g
    }, facing_left=False)
    
    fighter2_images = {
        'idle': assets.fighter2,
        'punch': assets.fighter2_punch,
        'kick': assets.fighter2_kick
    }
    fighter2 = Fighter(500, 300, fighter2_images, {
        'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP,
        'punch': pygame.K_k, 'kick': pygame.K_l
    }, facing_left=True)

    font = pygame.font.Font(None, 40)
    small_font = pygame.font.Font(None, 24)
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0 # Quit to launcher

        # Update fighters
        fighter1.move(fighter2)
        fighter2.move(fighter1)

        # --- Drawing ---
        screen.blit(assets.background, (0, 0))
        
        # Health bars & Player Info
        # Player 1
        draw_text("Player 1", font, WHITE, screen, 170, 15)
        pygame.draw.rect(screen, RED, (20, 40, 300, 30))
        pygame.draw.rect(screen, GREEN, (20, 40, fighter1.health * 3, 30))
        draw_text("Controls: WASD, F: Punch, G: Kick", small_font, WHITE, screen, 170, 80)

        # Player 2
        draw_text("Player 2", font, WHITE, screen, SCREEN_WIDTH - 170, 15)
        pygame.draw.rect(screen, RED, (SCREEN_WIDTH - 320, 40, 300, 30))
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 320, 40, fighter2.health * 3, 30))
        draw_text("Controls: Arrows, K: Punch, L: Kick", small_font, WHITE, screen, SCREEN_WIDTH - 170, 80)


        fighter1.draw(screen)
        fighter2.draw(screen)

        # Check for game over
        if fighter1.health <= 0 or fighter2.health <= 0:
            winner = "Player 2" if fighter1.health <= 0 else "Player 1"
            draw_text(f"{winner} WINS!", font, YELLOW, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            game_over = True

        pygame.display.flip()
        clock.tick(FPS)

        if game_over:
            pygame.time.wait(3000)

    return 0

def get_instructions():
    """Returns a list of instructions for the game."""
    return [
        "Player 1: WASD to move, F to punch, G to kick.",
        "Player 2: Arrow keys to move, K to punch, L to kick.",
        "Last fighter standing wins!",
    ]

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Beat 'em Up")
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()
