"""
Pygame implementation of the classic arcade game Galaga.
"""

import pygame
import sys
import random
import math

from config import BLACK, WHITE, RED, GREEN, BLUE
from utils import draw_text, pause_menu, settings_menu, Particle, create_explosion
import scores

# --- Initialization ---
pygame.init()

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

PLAYER_SIZE = 50
PLAYER_SPEED = 7
PLAYER_BULLET_SPEED = 10

ENEMY_SIZE = 40
ENEMY_SPEED_X_INITIAL = 2
ENEMY_SPEED_Y_INITIAL = 15
ENEMY_FIRE_RATE_INITIAL = 150 # Lower is faster
ENEMY_BULLET_SPEED = 7

BULLET_WIDTH, BULLET_HEIGHT = 5, 15

# Level configurations
LEVEL_CONFIGS = {
    1: {'enemy_speed_x': 2, 'enemy_speed_y': 15, 'enemy_fire_rate': 150, 'num_enemies': 10, 'color': (255, 0, 0)},
    2: {'enemy_speed_x': 3, 'enemy_speed_y': 20, 'enemy_fire_rate': 120, 'num_enemies': 15, 'color': (0, 255, 0)},
    3: {'enemy_speed_x': 4, 'enemy_speed_y': 25, 'enemy_fire_rate': 100, 'num_enemies': 20, 'color': (0, 0, 255)},
}

def create_starfield(num_stars):
    """Creates a list of stars for the background."""
    stars = []
    for _ in range(num_stars):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        speed = random.uniform(0.5, 2)
        stars.append({'x': x, 'y': y, 'speed': speed})
    return stars

def draw_starfield(screen, stars):
    """Draws and updates the starfield."""
    for star in stars:
        star['y'] += star['speed']
        if star['y'] > SCREEN_HEIGHT:
            star['y'] = 0
            star['x'] = random.randint(0, SCREEN_WIDTH)
        pygame.draw.circle(screen, (150, 150, 150), (int(star['x']), int(star['y'])), 1)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - PLAYER_SIZE // 2, SCREEN_HEIGHT - 70, PLAYER_SIZE, PLAYER_SIZE)
        self.lives = 3

    def move(self, dx):
        self.rect.x += dx
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH

    def draw(self, screen):
        # Main body
        pygame.draw.rect(screen, GREEN, self.rect, border_radius=5)
        # Cockpit
        pygame.draw.polygon(screen, WHITE, [
            (self.rect.centerx, self.rect.top),
            (self.rect.left + self.rect.width * 0.2, self.rect.centery),
            (self.rect.right - self.rect.width * 0.2, self.rect.centery)
        ])

class Bullet:
    def __init__(self, x, y, speed, color):
        self.rect = pygame.Rect(x - BULLET_WIDTH // 2, y, BULLET_WIDTH, BULLET_HEIGHT)
        self.speed = speed
        self.color = color

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=3)

class Enemy:
    def __init__(self, x, y, speed_x, speed_y, direction, color):
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.direction = direction # 1 for right, -1 for left
        self.animation_timer = 0
        self.color = color

    def update(self):
        self.rect.x += self.speed_x * self.direction
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1
            self.rect.y += self.speed_y
        self.animation_timer += 1

    def draw(self, screen):
        # Simple animation
        offset_y = math.sin(self.animation_timer * 0.1) * 5
        
        # Main body with gradient
        top_color = (min(self.color[0] + 50, 255), min(self.color[1] + 50, 255), min(self.color[2] + 50, 255))
        bottom_color = self.color
        pygame.draw.rect(screen, top_color, (self.rect.left, self.rect.top + offset_y, self.rect.width, self.rect.height // 2), border_top_left_radius=5, border_top_right_radius=5)
        pygame.draw.rect(screen, bottom_color, (self.rect.left, self.rect.centery + offset_y, self.rect.width, self.rect.height // 2), border_bottom_left_radius=5, border_bottom_right_radius=5)

        # Wings
        wing_color = (max(self.color[0] - 50, 0), max(self.color[1] - 50, 0), max(self.color[2] - 50, 0))
        pygame.draw.polygon(screen, wing_color, [
            (self.rect.left - 10, self.rect.bottom + offset_y),
            (self.rect.left + 10, self.rect.centery + offset_y),
            (self.rect.left, self.rect.centery + 10 + offset_y)
        ])
        pygame.draw.polygon(screen, wing_color, [
            (self.rect.right + 10, self.rect.bottom + offset_y),
            (self.rect.right - 10, self.rect.centery + offset_y),
            (self.rect.right, self.rect.centery + 10 + offset_y)
        ])

        # Cockpit
        cockpit_color = (200, 200, 255)
        pygame.draw.ellipse(screen, cockpit_color, pygame.Rect(self.rect.centerx - 5, self.rect.top + 5 + offset_y, 10, 15))

def create_enemies(num_enemies, enemy_speed_x, enemy_speed_y, color):
    enemies = []
    rows = (num_enemies + 10 - 1) // 10 # Calculate rows needed
    for row in range(rows):
        for col in range(10):
            if len(enemies) < num_enemies:
                x = col * (ENEMY_SIZE + 10) + 50
                y = row * (ENEMY_SIZE + 10) + 50
                enemies.append(Enemy(x, y, enemy_speed_x, enemy_speed_y, 1, color))
    return enemies

def main_menu(screen, clock, font, small_font):
    """
    Displays the main menu for Galaga.

    Args:
        screen (pygame.Surface): The screen to draw the menu on.
        clock (pygame.time.Clock): The Pygame clock object.
        font (pygame.font.Font): The font for the title.
        small_font (pygame.font.Font): The font for the buttons.

    Returns:
        str: The action selected by the user ('play', 'settings', or 'quit').
    """
    # Colors
    BACKGROUND_COLOR = (30, 10, 10) # Darker red
    TEXT_COLOR = (255, 255, 255) # White
    HIGHLIGHT_COLOR = (255, 0, 0) # Red
    BUTTON_COLOR = (50, 50, 50) # Dark Gray
    BUTTON_HOVER_COLOR = (80, 80, 80) # Lighter Gray on hover
    BORDER_COLOR = (150, 150, 150) # Medium Gray

    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("Galaga", font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        
        mx, my = pygame.mouse.get_pos()

        # Button dimensions and spacing
        button_width = 250
        button_height = 60
        button_spacing = 20

        settings_y = SCREEN_HEIGHT / 2 - 50
        start_y = settings_y + button_height + button_spacing
        quit_y = start_y + button_height + button_spacing

        settings_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, settings_y, button_width, button_height)
        start_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, start_y, button_width, button_height)
        quit_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, quit_y, button_width, button_height)

        buttons = [
            {"text": "Settings", "rect": settings_button_rect, "action": "settings"},
            {"text": "Start Game", "rect": start_button_rect, "action": "play"},
            {"text": "Back to Menu", "rect": quit_button_rect, "action": "quit"}
        ]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        if button["action"] == "settings":
                            new_volume, status = settings_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT, pygame.mixer.music.get_volume())
                            if status == 'quit': return 'quit'
                        else:
                            return button["action"]

        # Draw buttons with hover effect
        for button in buttons:
            current_button_color = BUTTON_HOVER_COLOR if button["rect"].collidepoint(mx, my) else BUTTON_COLOR
            pygame.draw.rect(screen, current_button_color, button["rect"], border_radius=10)
            pygame.draw.rect(screen, BORDER_COLOR, button["rect"], 2, border_radius=10)
            draw_text(button["text"], small_font, TEXT_COLOR, screen, button["rect"].centerx, button["rect"].centery)

        pygame.display.flip()
        clock.tick(15)

def game_loop(screen, clock, font, level, total_score=0):
    pygame.display.set_caption(f"Galaga - Level {level}")
    player = Player()
    player_bullets = []
    enemy_bullets = []
    score = total_score
    particles = []
    stars = create_starfield(100)

    # Get level configurations
    config = LEVEL_CONFIGS[level]
    enemy_speed_x = config['enemy_speed_x']
    enemy_speed_y = config['enemy_speed_y']
    enemy_fire_rate = config['enemy_fire_rate']
    num_enemies = config['num_enemies']
    enemy_color = config['color']

    enemies = create_enemies(num_enemies, enemy_speed_x, enemy_speed_y, enemy_color)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score, 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player_bullets.append(Bullet(player.rect.centerx, player.rect.top, -PLAYER_BULLET_SPEED, WHITE))
                if event.key == pygame.K_p:
                    pause_choice = pause_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT)
                    if pause_choice == 'quit': return score, 'quit'

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-PLAYER_SPEED)
            particles.append(Particle(player.rect.right, player.rect.centery, (200, 200, 255), 2, 15, 2, 0))
        if keys[pygame.K_RIGHT]:
            player.move(PLAYER_SPEED)
            particles.append(Particle(player.rect.left, player.rect.centery, (200, 200, 255), 2, 15, -2, 0))

        # Update bullets
        for bullet in player_bullets[:]:
            bullet.update()
            if bullet.rect.bottom < 0: player_bullets.remove(bullet)

        for bullet in enemy_bullets[:]:
            bullet.update()
            if bullet.rect.top > SCREEN_HEIGHT: enemy_bullets.remove(bullet)

        # Update enemies and enemy firing
        for enemy in enemies[:]:
            enemy.update()
            if random.randint(1, enemy_fire_rate) == 1: # Enemy fires
                enemy_bullets.append(Bullet(enemy.rect.centerx, enemy.rect.bottom, ENEMY_BULLET_SPEED, RED))

        # Collisions: Player bullets and enemies
        for p_bullet in player_bullets[:]:
            for enemy in enemies[:]:
                if p_bullet.rect.colliderect(enemy.rect):
                    player_bullets.remove(p_bullet)
                    enemies.remove(enemy)
                    score += 100
                    create_explosion(particles, enemy.rect.centerx, enemy.rect.centery, RED)
                    break
        
        # Collisions: Enemy bullets and player
        for e_bullet in enemy_bullets[:]:
            if e_bullet.rect.colliderect(player.rect):
                enemy_bullets.remove(e_bullet)
                player.lives -= 1
                create_explosion(particles, player.rect.centerx, player.rect.centery, GREEN)
                if player.lives <= 0: return score, 'game_over'

        # Collisions: Enemies and player (if they reach bottom)
        for enemy in enemies[:]:
            if enemy.rect.colliderect(player.rect):
                player.lives = 0 # Instant game over if enemy touches player
                create_explosion(particles, player.rect.centerx, player.rect.centery, GREEN, 50)
                return score, 'game_over'

        # Check for win condition
        if not enemies:
            return score, 'next_level'

        # Update particles
        for p in particles:
            p.update()
        particles = [p for p in particles if p.life > 0]

        # Drawing
        screen.fill(BLACK)
        draw_starfield(screen, stars)
        player.draw(screen)
        for bullet in player_bullets: bullet.draw(screen)
        for enemy in enemies: enemy.draw(screen)
        for bullet in enemy_bullets: bullet.draw(screen)
        for p in particles: p.draw(screen)

        # Draw UI
        draw_text(f"Score: {score}", font, WHITE, screen, 100, 20)
        draw_text(f"Lives: {player.lives}", font, WHITE, screen, SCREEN_WIDTH - 100, 20)
        draw_text(f"Level: {level}", font, WHITE, screen, SCREEN_WIDTH / 2, 20)

        pygame.display.flip()
        clock.tick(60)


def congratulations_screen(screen, clock, font, final_score):
    """
    Displays a congratulations screen when the player beats all levels.

    Args:
        screen (pygame.Surface): The screen to draw on.
        clock (pygame.time.Clock): The Pygame clock object.
        font (pygame.font.Font): The font for the text.
        final_score (int): The player's final score.
    """
    # Colors for the congratulations screen UI.
    BACKGROUND_COLOR = (30, 10, 10)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (255, 0, 0) # Red
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    title_font = pygame.font.Font(None, 70)
    score_font = pygame.font.Font(None, 50)
    button_font = pygame.font.Font(None, 40)

    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("CONGRATULATIONS!", title_font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3 - 50)
        draw_text(f"You beat Galaga!", score_font, TEXT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3 + 20)
        draw_text(f"Final Score: {final_score}", score_font, TEXT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3 + 80)

        mx, my = pygame.mouse.get_pos()

        # Button dimensions and spacing
        button_width = 250
        button_height = 60
        button_spacing = 20

        back_to_menu_y = SCREEN_HEIGHT / 2 + 100

        back_to_menu_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, back_to_menu_y, button_width, button_height)

        buttons = [
            {"text": "Back to Menu", "rect": back_to_menu_button_rect, "action": "quit"}
        ]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        return button["action"]

        # Draw buttons with hover effect
        for button in buttons:
            current_button_color = BUTTON_HOVER_COLOR if button["rect"].collidepoint(mx, my) else BUTTON_COLOR
            pygame.draw.rect(screen, current_button_color, button["rect"], border_radius=10)
            pygame.draw.rect(screen, BORDER_COLOR, button["rect"], 2, border_radius=10)
            draw_text(button["text"], button_font, TEXT_COLOR, screen, button["rect"].centerx, button["rect"].centery)

        pygame.display.flip()
        clock.tick(15)

def end_screen(screen, clock, font, message):
    """
    Displays the end screen with a message and options to play again or quit.

    Args:
        screen (pygame.Surface): The screen to draw on.
        clock (pygame.time.Clock): The Pygame clock object.
        font (pygame.font.Font): The font for the text.
        message (str): The message to display (e.g., "Game Over!").

    Returns:
        str: The action selected by the user ('play_again' or 'quit').
    """
    # Colors for the end screen UI.
    BACKGROUND_COLOR = (30, 10, 10)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (255, 0, 0) # Red
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    title_font = pygame.font.Font(None, 60)
    button_font = pygame.font.Font(None, 40)

    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text(message, title_font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)

        mx, my = pygame.mouse.get_pos()

        # Button dimensions and spacing
        button_width = 250
        button_height = 60
        button_spacing = 20

        play_again_y = SCREEN_HEIGHT / 2 + 20
        quit_y = play_again_y + button_height + button_spacing

        play_again_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, play_again_y, button_width, button_height)
        quit_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, quit_y, button_width, button_height)

        buttons = [
            {"text": "Play Again", "rect": play_again_button_rect, "action": "play_again"},
            {"text": "Back to Menu", "rect": quit_button_rect, "action": "quit"}
        ]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        return button["action"]

        # Draw buttons with hover effect
        for button in buttons:
            current_button_color = BUTTON_HOVER_COLOR if button["rect"].collidepoint(mx, my) else BUTTON_COLOR
            pygame.draw.rect(screen, current_button_color, button["rect"], border_radius=10)
            pygame.draw.rect(screen, BORDER_COLOR, button["rect"], 2, border_radius=10)
            draw_text(button["text"], button_font, TEXT_COLOR, screen, button["rect"].centerx, button["rect"].centery)

        pygame.display.flip()
        clock.tick(15)

def next_level_screen(screen, clock, font, level, score):
    """
    Displays a screen between levels with a "Continue" button.

    Args:
        screen (pygame.Surface): The screen to draw on.
        clock (pygame.time.Clock): The Pygame clock object.
        font (pygame.font.Font): The font for the text.
        level (int): The level that was just completed.
        score (int): The player's current score.

    Returns:
        str: The action selected by the user ('continue' or 'quit').
    """
    # Colors for the next level screen UI.
    BACKGROUND_COLOR = (10, 10, 30) # Darker blue
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (0, 255, 255) # Cyan
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

        # Button dimensions and spacing
        button_width = 250
        button_height = 60
        button_spacing = 20

        continue_y = SCREEN_HEIGHT / 2 + 100
        quit_y = continue_y + button_height + button_spacing

        continue_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, continue_y, button_width, button_height)
        quit_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, quit_y, button_width, button_height)

        buttons = [
            {"text": "Continue", "rect": continue_button_rect, "action": "continue"},
            {"text": "Back to Menu", "rect": quit_button_rect, "action": "quit"}
        ]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        return button["action"]

        # Draw buttons with hover effect
        for button in buttons:
            current_button_color = BUTTON_HOVER_COLOR if button["rect"].collidepoint(mx, my) else BUTTON_COLOR
            pygame.draw.rect(screen, current_button_color, button["rect"], border_radius=10)
            pygame.draw.rect(screen, BORDER_COLOR, button["rect"], 2, border_radius=10)
            draw_text(button["text"], button_font, TEXT_COLOR, screen, button["rect"].centerx, button["rect"].centery)

        pygame.display.flip()
        clock.tick(15)

def run_game(screen, clock):
    """
    Main function to manage the game states for Galaga.

    Args:
        screen (pygame.Surface): The main screen surface.
        clock (pygame.time.Clock): The Pygame clock object.
    """
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)

    while True:
        menu_choice = main_menu(screen, clock, font, small_font)
        if menu_choice == 'quit':
            return 0

        current_level = 1
        total_score = 0
        game_outcome = None

        while current_level <= 3:
            level_score, status = game_loop(screen, clock, small_font, current_level, total_score)
            total_score = level_score # Update cumulative score

            if status == 'next_level':
                current_level += 1
                if current_level > 3:
                    game_outcome = 'win'
                    break
                else:
                    next_level_choice = next_level_screen(screen, clock, small_font, current_level - 1, total_score)
                    if next_level_choice == 'quit':
                        game_outcome = 'quit'
                        break
            elif status == 'game_over':
                game_outcome = 'game_over'
                break
            elif status == 'quit':
                game_outcome = 'quit'
                break

        scores.save_score("Galaga", total_score)

        if game_outcome == 'win':
            congratulations_screen(screen, clock, font, total_score)
        elif game_outcome == 'game_over':
            end_choice = end_screen(screen, clock, font, f"Game Over! Score: {total_score}")
            if end_choice == 'quit':
                return total_score
        elif game_outcome == 'quit':
            return total_score

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()