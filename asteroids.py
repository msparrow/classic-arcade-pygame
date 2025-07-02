"""
Pygame implementation of the classic arcade game Asteroids.

This script contains the game logic for Asteroids, including the player ship,
- bullets, asteroids, and collision detection. It also features a main menu and an end screen.
"""

import pygame
import sys
import random
import math

# Import shared modules and constants.
from config import BLACK, WHITE, BLUE
from utils import draw_text, pause_menu, settings_menu
import scores

# --- Initialization ---
# Initialize all imported Pygame modules.
pygame.init()

# --- Constants ---
# Screen dimensions.
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Player properties.
PLAYER_SIZE, PLAYER_ROTATION_SPEED, PLAYER_ACCELERATION, PLAYER_FRICTION = 20, 5, 0.2, 0.99
# Bullet properties.
BULLET_SPEED, BULLET_LIFESPAN = 10, 40
# Asteroid properties.
ASTEROID_SPEED, ASTEROID_INITIAL_COUNT = 2, 5

class Player:
    """
    Represents the player's ship.
    """
    def __init__(self):
        """
        Initializes a Player object.
        """
        self.pos = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.vel = pygame.Vector2(0, 0)
        self.angle = 0
        self.shield_active = False
        self.shield_timer = 0
        self.shield_cooldown = 10000  # 10 seconds
        self.last_shield_time = -self.shield_cooldown

    def activate_shield(self):
        """
        Activates the player's shield if it's not on cooldown.
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shield_time > self.shield_cooldown:
            self.shield_active = True
            self.shield_timer = current_time
            self.last_shield_time = current_time

    def update(self):
        """
        Updates the player's position and handles screen wrapping and shield duration.
        """
        self.pos += self.vel
        self.vel *= PLAYER_FRICTION
        # Screen wrapping.
        if self.pos.x > SCREEN_WIDTH: self.pos.x = 0
        if self.pos.x < 0: self.pos.x = SCREEN_WIDTH
        if self.pos.y > SCREEN_HEIGHT: self.pos.y = 0
        if self.pos.y < 0: self.pos.y = SCREEN_HEIGHT

        # Shield timer.
        if self.shield_active and pygame.time.get_ticks() - self.shield_timer > 3000:  # 3 seconds
            self.shield_active = False

    def draw(self, surface):
        """
        Draws the player's ship and shield on the screen.

        Args:
            surface (pygame.Surface): The surface to draw on.
        """
        angle_rad = math.radians(self.angle)
        points = [
            (self.pos.x + PLAYER_SIZE * math.cos(angle_rad), self.pos.y - PLAYER_SIZE * math.sin(angle_rad)),
            (self.pos.x + PLAYER_SIZE * math.cos(angle_rad + 2.5) / 2, self.pos.y - PLAYER_SIZE * math.sin(angle_rad + 2.5) / 2),
            (self.pos.x + PLAYER_SIZE * math.cos(angle_rad - 2.5) / 2, self.pos.y - PLAYER_SIZE * math.sin(angle_rad - 2.5) / 2)
        ]
        pygame.draw.polygon(surface, WHITE, points, 1)
        if self.shield_active:
            pygame.draw.circle(surface, BLUE, (int(self.pos.x), int(self.pos.y)), PLAYER_SIZE * 1.5, 1)

class Bullet:
    """
    Represents a bullet fired by the player.
    """
    def __init__(self, pos, angle):
        """
        Initializes a Bullet object.

        Args:
            pos (pygame.Vector2): The initial position of the bullet.
            angle (float): The angle at which the bullet is fired.
        """
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(BULLET_SPEED, 0).rotate(-angle)
        self.lifespan = BULLET_LIFESPAN

    def update(self):
        """
        Updates the bullet's position and decreases its lifespan.
        """
        self.pos += self.vel
        self.lifespan -= 1

    def draw(self, surface):
        """
        Draws the bullet on the screen.

        Args:
            surface (pygame.Surface): The surface to draw on.
        """
        pygame.draw.circle(surface, WHITE, (int(self.pos.x), int(self.pos.y)), 2)

class Asteroid:
    """
    Represents an asteroid.
    """
    def __init__(self, pos=None, size=3):
        """
        Initializes an Asteroid object.

        Args:
            pos (pygame.Vector2, optional): The initial position of the asteroid. Defaults to None.
            size (int, optional): The size of the asteroid (1, 2, or 3). Defaults to 3.
        """
        self.pos = pygame.Vector2(pos) if pos else pygame.Vector2(random.randrange(SCREEN_WIDTH), random.randrange(SCREEN_HEIGHT))
        self.vel = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * ASTEROID_SPEED
        self.size = size
        self.radius = self.size * 15

    def update(self):
        """
        Updates the asteroid's position and handles screen wrapping.
        """
        self.pos += self.vel
        # Screen wrapping.
        if self.pos.x > SCREEN_WIDTH + self.radius: self.pos.x = -self.radius
        if self.pos.x < -self.radius: self.pos.x = SCREEN_WIDTH + self.radius
        if self.pos.y > SCREEN_HEIGHT + self.radius: self.pos.y = -self.radius
        if self.pos.y < -self.radius: self.pos.y = SCREEN_HEIGHT + self.radius

    def draw(self, surface):
        """
        Draws the asteroid on the screen.

        Args:
            surface (pygame.Surface): The surface to draw on.
        """
        pygame.draw.circle(surface, WHITE, (int(self.pos.x), int(self.pos.y)), self.radius, 1)

def main_menu(screen, clock, font, small_font):
    """
    Displays the main menu for Asteroids.

    Args:
        screen (pygame.Surface): The screen to draw the menu on.
        clock (pygame.time.Clock): The Pygame clock object.
        font (pygame.font.Font): The font for the title.
        small_font (pygame.font.Font): The font for the buttons.

    Returns:
        str: The action selected by the user ('play', 'settings', or 'quit').
    """
    # Colors for the main menu UI.
    BACKGROUND_COLOR = (10, 10, 30)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (0, 255, 255)
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    # Main loop for the menu.
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("Asteroids", font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)

        mx, my = pygame.mouse.get_pos()

        # Define button properties.
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

        # Event handling for the menu.
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

        # Draw buttons with hover effects.
        for button in buttons:
            current_button_color = BUTTON_HOVER_COLOR if button["rect"].collidepoint(mx, my) else BUTTON_COLOR
            pygame.draw.rect(screen, current_button_color, button["rect"], border_radius=10)
            pygame.draw.rect(screen, BORDER_COLOR, button["rect"], 2, border_radius=10)
            draw_text(button["text"], small_font, TEXT_COLOR, screen, button["rect"].centerx, button["rect"].centery)

        pygame.display.flip()
        clock.tick(15)

def game_loop(screen, clock, font):
    """
    Runs the main game loop for Asteroids.

    Args:
        screen (pygame.Surface): The main screen surface to draw on.
        clock (pygame.time.Clock): The Pygame clock object for controlling the frame rate.
        font (pygame.font.Font): The font for the UI elements.

    Returns:
        int: The final score of the player.
    """
    pygame.display.set_caption("Asteroids")
    font = pygame.font.Font(None, 36)
    # Initialize game objects.
    player = Player()
    bullets, asteroids = [], [Asteroid() for _ in range(ASTEROID_INITIAL_COUNT)]
    score, game_over = 0, False

    # Main game loop.
    while True:
        # Event handling.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score
            if event.type == pygame.KEYDOWN:
                if not game_over and event.key == pygame.K_SPACE and len(bullets) < 5:
                    bullets.append(Bullet(player.pos, player.angle))
                if event.key == pygame.K_p:
                    # Pause the game.
                    pause_choice = pause_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT)
                    if pause_choice == 'quit':
                        return score
                if event.key == pygame.K_s:
                    # Activate the shield.
                    player.activate_shield()

        if not game_over:
            # Player movement.
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: player.angle += PLAYER_ROTATION_SPEED
            if keys[pygame.K_RIGHT]: player.angle -= PLAYER_ROTATION_SPEED
            if keys[pygame.K_UP]: player.vel += pygame.Vector2(PLAYER_ACCELERATION, 0).rotate(-player.angle)

            # Update game objects.
            player.update()
            for b in bullets[:]:
                b.update()
                if b.lifespan <= 0: bullets.remove(b)
            for a in asteroids: a.update()

            # Collision detection: bullets and asteroids.
            for b in bullets[:]:
                for a in asteroids[:]:
                    if b.pos.distance_to(a.pos) < a.radius:
                        bullets.remove(b)
                        asteroids.remove(a)
                        score += 10 * (4 - a.size)
                        # Split asteroid into smaller pieces.
                        if a.size > 1:
                            asteroids.extend([Asteroid(a.pos, a.size - 1), Asteroid(a.pos, a.size - 1)])
                        break

            # Collision detection: player and asteroids.
            for a in asteroids:
                if player.pos.distance_to(a.pos) < a.radius + PLAYER_SIZE / 2:
                    if not player.shield_active:
                        game_over = True
                    else:
                        # If shield is active, destroy the asteroid.
                        asteroids.remove(a)
                        score += 10 * (4 - a.size)
                        if a.size > 1:
                            asteroids.extend([Asteroid(a.pos, a.size - 1), Asteroid(a.pos, a.size - 1)])

        # --- Drawing ---
        screen.fill(BLACK)
        player.draw(screen)
        for b in bullets: b.draw(screen)
        for a in asteroids: a.draw(screen)

        # Draw score.
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Game over and win conditions.
        if game_over:
            end_choice = end_screen(screen, clock, font, f"Game Over! Score: {score}")
            if end_choice == 'quit':
                return score
            # Restart the game.
            player = Player()
            bullets, asteroids = [], [Asteroid() for _ in range(ASTEROID_INITIAL_COUNT)]
            score, game_over = 0, False
        if not asteroids:
            end_choice = end_screen(screen, clock, font, f"You Win! Score: {score}")
            if end_choice == 'quit':
                return score
            # Restart the game.
            player = Player()
            bullets, asteroids = [], [Asteroid() for _ in range(ASTEROID_INITIAL_COUNT)]
            score, game_over = 0, False

        pygame.display.flip()
        clock.tick(60)

def run_game(screen, clock):
    """
    Main function to manage the game states for Asteroids.

    Args:
        screen (pygame.Surface): The main screen surface.
        clock (pygame.time.Clock): The Pygame clock object.
    """
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)
    # Main state machine loop.
    while True:
        menu_choice = main_menu(screen, clock, font, small_font)
        if menu_choice == 'quit':
            return 0
        final_score = game_loop(screen, clock, font)
        scores.save_score("Asteroids", final_score)

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
    BACKGROUND_COLOR = (10, 10, 30)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (0, 255, 255)
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    title_font = pygame.font.Font(None, 60)
    button_font = pygame.font.Font(None, 40)

    # Main loop for the end screen.
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text(message, title_font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)

        mx, my = pygame.mouse.get_pos()

        # Define button properties.
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

        # Event handling for the end screen.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        return button["action"]

        # Draw buttons with hover effects.
        for button in buttons:
            current_button_color = BUTTON_HOVER_COLOR if button["rect"].collidepoint(mx, my) else BUTTON_COLOR
            pygame.draw.rect(screen, current_button_color, button["rect"], border_radius=10)
            pygame.draw.rect(screen, BORDER_COLOR, button["rect"], 2, border_radius=10)
            draw_text(button["text"], button_font, TEXT_COLOR, screen, button["rect"].centerx, button["rect"].centery)

        pygame.display.flip()
        clock.tick(15)

if __name__ == "__main__":
    # This block runs when the script is executed directly.
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()
