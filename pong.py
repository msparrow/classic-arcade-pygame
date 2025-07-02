"""
Pygame implementation of the classic arcade game Pong.

This script contains the game logic for Pong, including player and AI paddle movement,
ball physics, and scoring. It also features a main menu and an end screen.
"""

import pygame
import sys
import random

# Import shared modules and constants.
from config import BLACK, WHITE, DEFAULT_MUSIC_VOLUME
from utils import draw_text, pause_menu, settings_menu, Particle, ScreenShaker, create_explosion
import scores

# --- Initialization ---
# Initialize all imported Pygame modules.
pygame.init()

# --- Constants ---
# Screen dimensions.
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
# Paddle dimensions.
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
# Ball dimensions.
BALL_SIZE = 15
# Paddle speeds.
PADDLE_SPEED = 7
AI_PADDLE_SPEED = 6
# The score required to win the game.
WINNING_SCORE = 5

def main_menu(screen, clock, font, small_font):
    """
    Displays the main menu for Pong.

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
    HIGHLIGHT_COLOR = (0, 255, 0)
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    # Main loop for the menu.
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("Pong", font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)

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

def draw_retro_background(screen):
    """Draws a retro-style holographic grid background."""
    screen.fill((10, 10, 30)) # Dark Blue
    # Horizontal lines
    for i in range(0, SCREEN_HEIGHT, 20):
        pygame.draw.line(screen, (20, 20, 50), (0, i), (SCREEN_WIDTH, i), 1)
    # Vertical lines
    for i in range(0, SCREEN_WIDTH, 20):
        pygame.draw.line(screen, (20, 20, 50), (i, 0), (i, SCREEN_HEIGHT), 1)
    # Center line
    pygame.draw.line(screen, (100, 100, 100), (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)

def game_loop(screen, clock, font, sounds):
    """
    Runs the main game loop for Pong.

    Args:
        screen (pygame.Surface): The main screen surface to draw on.
        clock (pygame.time.Clock): The Pygame clock object for controlling the frame rate.
        font (pygame.font.Font): The font for the score display.
        sounds (dict): A dictionary of sound effects.

    Returns:
        tuple: A tuple containing the winner message and the final score.
    """
    # Initialize paddles and ball.
    player_paddle = pygame.Rect(50, SCREEN_HEIGHT / 2 - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ai_paddle = pygame.Rect(SCREEN_WIDTH - 50 - PADDLE_WIDTH, SCREEN_HEIGHT / 2 - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(SCREEN_WIDTH / 2 - BALL_SIZE / 2, SCREEN_HEIGHT / 2 - BALL_SIZE / 2, BALL_SIZE, BALL_SIZE)

    # Initialize ball speed.
    ball_speed_x = 7 * random.choice((1, -1))
    ball_speed_y = 7 * random.choice((1, -1))

    # Initialize scores.
    player_score, ai_score = 0, 0

    # Effects
    particles = []
    screen_shaker = None
    hit_flash = 0

    # Main game loop.
    running = True
    while running:
        # Event handling.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit', player_score
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                # Pause the game.
                pause_choice = pause_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT)
                if pause_choice == 'quit':
                    return player_score, 'quit'

        # Player movement.
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN]:
            player_paddle.y += PADDLE_SPEED

        # Keep player paddle on the screen.
        player_paddle.y = max(0, min(player_paddle.y, SCREEN_HEIGHT - PADDLE_HEIGHT))

        # Ball movement.
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Ball collision with top and bottom walls.
        if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
            sounds['wall_hit'].play()
            ball_speed_y *= -1

        # Ball collision with paddles.
        if ball.colliderect(player_paddle) or ball.colliderect(ai_paddle):
            sounds['paddle_hit'].play()
            ball_speed_x *= -1.1  # Increase speed on hit.
            ball_speed_y *= 1.1
            hit_flash = 10
            create_explosion(particles, ball.centerx, ball.centery, (255, 255, 0))

        # Scoring.
        if ball.left <= 0:
            ai_score += 1
            ball.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            ball_speed_x = 7 * random.choice((1, -1))
            ball_speed_y = 7 * random.choice((1, -1))
            sounds['score_point'].play()
            screen_shaker = ScreenShaker(intensity=5, duration=15)
        if ball.right >= SCREEN_WIDTH:
            player_score += 1
            ball.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            ball_speed_x = 7 * random.choice((1, -1))
            ball_speed_y = 7 * random.choice((1, -1))
            sounds['score_point'].play()
            screen_shaker = ScreenShaker(intensity=5, duration=15)

        # AI paddle movement.
        if ai_paddle.centery < ball.centery:
            ai_paddle.y += AI_PADDLE_SPEED
        if ai_paddle.centery > ball.centery:
            ai_paddle.y -= AI_PADDLE_SPEED
        ai_paddle.y = max(0, min(ai_paddle.y, SCREEN_HEIGHT - PADDLE_HEIGHT))

        # Update particles
        for p in particles:
            p.update()
        particles = [p for p in particles if p.life > 0]
        particles.append(Particle(ball.centerx, ball.centery, (200, 200, 0), 3, 10, 0, 0))

        # --- Drawing ---
        screen_offset = (0, 0)
        if screen_shaker:
            screen_offset = screen_shaker.shake()
            if screen_shaker.timer >= screen_shaker.duration:
                screen_shaker = None
        
        temp_surface = screen.copy()
        draw_retro_background(temp_surface)
        
        pygame.draw.rect(temp_surface, (200, 200, 200), player_paddle)
        pygame.draw.rect(temp_surface, (200, 200, 200), ai_paddle)
        pygame.draw.ellipse(temp_surface, (255, 255, 0), ball)

        for p in particles:
            p.draw(temp_surface)

        draw_text(str(player_score), font, WHITE, temp_surface, SCREEN_WIDTH / 4, 50)
        draw_text(str(ai_score), font, WHITE, temp_surface, SCREEN_WIDTH * 3 / 4, 50)

        if hit_flash > 0:
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, hit_flash * 20))
            temp_surface.blit(flash_surface, (0, 0))
            hit_flash -= 1

        screen.blit(temp_surface, screen_offset)
        pygame.display.flip()
        clock.tick(60)

        # Check for a winner.
        if player_score >= WINNING_SCORE:
            return "Player Wins!", player_score
        if ai_score >= WINNING_SCORE:
            return "AI Wins!", ai_score


def end_screen(screen, clock, font, small_font, message):
    """
    Displays the end screen with a message and options to play again or quit.

    Args:
        screen (pygame.Surface): The screen to draw on.
        clock (pygame.time.Clock): The Pygame clock object.
        font (pygame.font.Font): The font for the title.
        small_font (pygame.font.Font): The font for the buttons.
        message (str): The message to display (e.g., "Player Wins!").

    Returns:
        str: The action selected by the user ('play_again' or 'quit').
    """
    # Colors for the end screen UI.
    BACKGROUND_COLOR = (10, 10, 30)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (0, 255, 0)
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

def run_game(screen, clock):
    """
    Main function to manage the game states for Pong.

    Args:
        screen (pygame.Surface): The main screen surface.
        clock (pygame.time.Clock): The Pygame clock object.
    """
    pygame.display.set_caption("Pong")
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)

    # Load sounds with error handling.
    try:
        hit_sound = pygame.mixer.Sound('assets/sounds/wall_hit.wav')
        sounds = {'paddle_hit': hit_sound, 'wall_hit': hit_sound, 'score_point': hit_sound}
    except pygame.error:
        print("Could not load sound for Pong. Game will be silent.")
        # Create dummy sound objects if loading fails.
        class DummySound:
            def play(self): pass
        sounds = {'paddle_hit': DummySound(), 'wall_hit': DummySound(), 'score_point': DummySound()}

    # Main state machine loop.
    while True:
        menu_choice = main_menu(screen, clock, font, small_font)
        if menu_choice == 'quit':
            return 0

        winner_message, final_score = game_loop(screen, clock, font, sounds)
        scores.save_score("Pong", final_score)
        if winner_message == 'quit':
            return final_score

        end_choice = end_screen(screen, clock, font, small_font, winner_message)
        if end_choice == 'quit':
            return final_score

if __name__ == "__main__":
    # This block runs when the script is executed directly.
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()
