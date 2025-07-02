"""
Pygame implementation of the classic arcade game Breakout.

This script contains the game logic for Breakout, including the paddle, ball, bricks,
- and power-ups. It also features a main menu and an end screen.
"""

import pygame
import sys
import random

# Import shared modules and constants.
from config import BLACK, WHITE, GREEN, BLUE
from utils import draw_text, pause_menu, settings_menu, Particle, create_explosion
import scores

# --- Initialization ---
# Initialize all imported Pygame modules.
pygame.init()

# --- Constants ---
# Screen dimensions.
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
# Paddle dimensions.
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 20
# Ball radius.
BALL_RADIUS = 10
# Paddle and ball speeds.
PADDLE_SPEED = 10
BALL_SPEED_INITIAL = 6

# Brick dimensions and layout.
BRICK_WIDTH, BRICK_HEIGHT = 75, 30
BRICK_ROWS, BRICK_COLS = 5, 10
BRICK_GAP = 5

# Power-up properties.
POWER_UP_SIZE = 20
POWER_UP_SPEED = 3
POWER_UP_CHANCE = 0.25  # 25% chance of a power-up dropping.

# Power-up types
POWER_UP_TYPES = {
    (255, 0, 0): 'extra_life',
    (255, 165, 0): 'slow_ball',
    (0, 255, 0): 'widen_paddle',
    (0, 0, 255): 'multi_ball',
    (128, 0, 128): 'fast_ball'
}

# Colors specific to Breakout.
PADDLE_COLOR = (0, 150, 255)
BALL_COLOR = (255, 255, 0)
BRICK_COLORS = [(255, 0, 0), (255, 165, 0), (0, 255, 0), (0, 0, 255), (128, 0, 128)]

class PowerUp:
    """
    Represents a power-up in the Breakout game.
    """
    def __init__(self, center_pos, type, color):
        """
        Initializes a PowerUp object.

        Args:
            center_pos (tuple): The center position of the power-up.
            type (str): The type of the power-up.
            color (tuple): The color of the power-up.
        """
        self.rect = pygame.Rect(center_pos[0] - POWER_UP_SIZE / 2, center_pos[1] - POWER_UP_SIZE / 2, POWER_UP_SIZE, POWER_UP_SIZE)
        self.type = type
        self.color = color

    def update(self):
        """
        Updates the position of the power-up.
        """
        self.rect.y += POWER_UP_SPEED

    def draw(self, screen):
        """
        Draws the power-up on the screen.

        Args:
            screen (pygame.Surface): The screen to draw on.
        """
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.Font(None, 20)
        text = font.render(self.type, True, WHITE)
        screen.blit(text, text.get_rect(center=self.rect.center))

def create_bricks(level):
    """
    Creates the grid of bricks based on the current level.

    Args:
        level (int): The current game level.

    Returns:
        list: A list of dictionaries, where each dictionary represents a brick.
    """
    bricks = []
    # Increase brick rows with level, up to a maximum
    num_rows = min(BRICK_ROWS + (level - 1), 8) # Max 8 rows for example
    for row in range(num_rows):
        for col in range(BRICK_COLS):
            x = col * (BRICK_WIDTH + BRICK_GAP) + (SCREEN_WIDTH - (BRICK_COLS * (BRICK_WIDTH + BRICK_GAP))) / 2
            y = row * (BRICK_HEIGHT + BRICK_GAP) + 50
            brick = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
            bricks.append({'rect': brick, 'color': BRICK_COLORS[row % len(BRICK_COLORS)]})
    return bricks

def main_menu(screen, clock, font, small_font):
    """
    Displays the main menu for Breakout.

    Args:
        screen (pygame.Surface): The screen to draw the menu on.
        clock (pygame.time.Clock): The Pygame clock object.
        font (pygame.font.Font): The font for the title.
        small_font (pygame.font.Font): The font for the buttons.

    Returns:
        str: The action selected by the user ('play', 'settings', or 'quit').
    """
    # Colors for the main menu UI.
    BACKGROUND_COLOR = (30, 10, 30)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (255, 165, 0)
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    # Main loop for the menu.
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("Breakout", font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)

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

def draw_dynamic_background(screen, level):
    """Draws a dynamic, level-themed background."""
    colors = [
        (10, 10, 30), (30, 10, 10), (10, 30, 10), (10, 10, 10), (30, 30, 10)
    ]
    base_color = colors[level - 1]
    screen.fill(base_color)
    # Add some subtle animated stars or particles
    for _ in range(10):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(1, 2)
        color = (min(255, base_color[0] + 50), min(255, base_color[1] + 50), min(255, base_color[2] + 50))
        pygame.draw.circle(screen, color, (x, y), size)

def game_loop(screen, clock, font, level, total_score=0):
    """
    Runs the main game loop for Breakout.

    Args:
        screen (pygame.Surface): The main screen surface to draw on.
        clock (pygame.time.Clock): The Pygame clock object for controlling the frame rate.
        font (pygame.font.Font): The font for the UI elements.
        level (int): The current game level.
        total_score (int): The cumulative score from previous levels.

    Returns:
        tuple: (score, status) where status is 'next_level', 'game_over', or 'quit'.
    """
    pygame.display.set_caption(f"Breakout - Level {level}")
    font = pygame.font.Font(None, 36)
    # Initialize game objects.
    paddle = pygame.Rect(SCREEN_WIDTH / 2 - PADDLE_WIDTH / 2, SCREEN_HEIGHT - 40, PADDLE_WIDTH, PADDLE_HEIGHT)
    balls = [pygame.Rect(SCREEN_WIDTH / 2 - BALL_RADIUS, paddle.y - BALL_RADIUS * 2, BALL_RADIUS * 2, BALL_RADIUS * 2)]
    
    # Adjust ball speed based on level
    current_ball_speed = BALL_SPEED_INITIAL + (level - 1) * 0.5
    ball_speeds = [[current_ball_speed, -current_ball_speed]]
    
    bricks = create_bricks(level)
    power_ups = []
    particles = []
    score = total_score # Start with cumulative score
    lives = 3 # Lives reset per level, or carry over? Let's carry over for now.

    # Power-up state.
    widen_power_up_active = False
    widen_timer = 0

    # Main game loop.
    while True:
        # Event handling.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score, 'quit'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                # Pause the game.
                pause_choice = pause_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT)
                if pause_choice == 'quit':
                    return score, 'quit'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                # Open the settings menu.
                new_volume, status = settings_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT, pygame.mixer.music.get_volume())
                if status == 'quit':
                    return score, 'quit'

        # Paddle movement.
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: paddle.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT]: paddle.x += PADDLE_SPEED
        paddle.x = max(0, min(paddle.x, SCREEN_WIDTH - paddle.width))

        # Ball movement and collision.
        for i, ball in enumerate(balls[:]):
            ball.x += ball_speeds[i][0]
            ball.y += ball_speeds[i][1]

            # Wall collision.
            if ball.left <= 0 or ball.right >= SCREEN_WIDTH: ball_speeds[i][0] *= -1
            if ball.top <= 0: ball_speeds[i][1] *= -1

            # Paddle collision.
            if ball.colliderect(paddle):
                ball_speeds[i][1] *= -1
                # Change ball direction based on where it hits the paddle.
                offset = (ball.centerx - paddle.centerx) / (paddle.width / 2)
                ball_speeds[i][0] = offset * current_ball_speed # Use current_ball_speed here
                create_explosion(particles, ball.centerx, ball.centery, PADDLE_COLOR, 10)

            # Brick collision.
            for brick_info in bricks[:]:
                if ball.colliderect(brick_info['rect']):
                    bricks.remove(brick_info)
                    ball_speeds[i][1] *= -1
                    score += 10
                    create_explosion(particles, brick_info['rect'].centerx, brick_info['rect'].centery, brick_info['color'], 30)
                    # Chance to spawn a power-up.
                    if random.random() < POWER_UP_CHANCE:
                        power_up_type = POWER_UP_TYPES.get(brick_info['color'])
                        if power_up_type:
                            power_ups.append(PowerUp(brick_info['rect'].center, power_up_type, brick_info['color']))
                    break

            # Ball out of bounds.
            if ball.top >= SCREEN_HEIGHT:
                balls.pop(i)
                ball_speeds.pop(i)
                break

        # Check for game over.
        if not balls:
            lives -= 1
            if lives <= 0:
                return score, 'game_over' # Game over for this attempt
            else:
                # Relaunch a single ball
                balls.append(pygame.Rect(paddle.centerx - BALL_RADIUS, paddle.y - BALL_RADIUS * 2, BALL_RADIUS * 2, BALL_RADIUS * 2))
                ball_speeds.append([current_ball_speed, -current_ball_speed])


        # Power-up handling.
        for power_up in power_ups[:]:
            power_up.update()
            if power_up.rect.colliderect(paddle):
                if power_up.type == 'widen_paddle':
                    # Widen paddle power-up.
                    paddle.width = PADDLE_WIDTH * 1.5
                    widen_power_up_active = True
                    widen_timer = pygame.time.get_ticks()
                elif power_up.type == 'multi_ball':
                    # Multi-ball power-up.
                    balls.append(pygame.Rect(paddle.centerx - BALL_RADIUS, paddle.y - BALL_RADIUS * 2, BALL_RADIUS * 2, BALL_RADIUS * 2))
                    ball_speeds.append([current_ball_speed, -current_ball_speed]) # Use current_ball_speed
                elif power_up.type == 'extra_life':
                    lives += 1
                elif power_up.type == 'slow_ball':
                    for speed in ball_speeds:
                        speed[0] *= 0.8
                        speed[1] *= 0.8
                elif power_up.type == 'fast_ball':
                    for speed in ball_speeds:
                        speed[0] *= 1.2
                        speed[1] *= 1.2
                power_ups.remove(power_up)
            elif power_up.rect.top > SCREEN_HEIGHT:
                power_ups.remove(power_up)

        # Widen power-up timer.
        if widen_power_up_active and pygame.time.get_ticks() - widen_timer > 10000:  # 10 seconds
            paddle.width = PADDLE_WIDTH
            widen_power_up_active = False

        # Update particles
        for p in particles:
            p.update()
        particles = [p for p in particles if p.life > 0]
        for ball in balls:
            particles.append(Particle(ball.centerx, ball.centery, (200, 200, 0), 4, 10, 0, 0))

        # Check for win condition.
        if not bricks:
            return score, 'next_level' # Level complete

        # --- Drawing ---
        draw_dynamic_background(screen, level)
        # Draw detailed paddle
        pygame.draw.rect(screen, PADDLE_COLOR, paddle, border_radius=5) # Main paddle body
        pygame.draw.rect(screen, tuple(min(255, c + 30) for c in PADDLE_COLOR), 
                         (paddle.x, paddle.y, paddle.width, 5), border_radius=5) # Top highlight
        
        # Draw detailed balls
        for ball in balls:
            pygame.draw.ellipse(screen, BALL_COLOR, ball) # Main ball body
            pygame.draw.circle(screen, WHITE, (ball.centerx - ball.width // 4, ball.centery - ball.height // 4), 
                               ball.width // 4) # Highlight
        
        for brick_info in bricks:
            pygame.draw.rect(screen, brick_info['color'], brick_info['rect'], border_radius=3)
            pygame.draw.rect(screen, tuple(min(255, c + 50) for c in brick_info['color']), brick_info['rect'].inflate(-6, -6))

        for power_up in power_ups:
            power_up.draw(screen)

        for p in particles:
            p.draw(screen)

        # Draw UI.
        draw_text(f"Score: {score}", font, WHITE, screen, 80, 20)
        draw_text(f"Lives: {lives}", font, WHITE, screen, SCREEN_WIDTH - 80, 20)
        draw_text(f"Level: {level}", font, WHITE, screen, SCREEN_WIDTH / 2, 20) # Display current level

        pygame.display.flip()
        clock.tick(60)

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
    BACKGROUND_COLOR = (30, 10, 30)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (255, 165, 0)
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
    BACKGROUND_COLOR = (30, 10, 30)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (255, 215, 0) # Gold
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    title_font = pygame.font.Font(None, 70)
    score_font = pygame.font.Font(None, 50)
    button_font = pygame.font.Font(None, 40)

    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("CONGRATULATIONS!", title_font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3 - 50)
        draw_text(f"You beat Breakout!", score_font, TEXT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3 + 20)
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

def run_game(screen, clock):
    """
    Main function to manage the game states for Breakout.

    Args:
        screen (pygame.Surface): The main screen surface.
        clock (pygame.time.Clock): The Pygame clock object.
    """
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)
    
    # Game loop for levels
    while True:
        menu_choice = main_menu(screen, clock, font, small_font)
        if menu_choice == 'quit':
            return 0 # Return 0 score when quitting from menu

        current_level = 1
        total_score = 0
        game_outcome = None

        while current_level <= 5:
            # Pass current level and cumulative score to game_loop
            level_score, status = game_loop(screen, clock, small_font, current_level, total_score)
            total_score = level_score # Update cumulative score

            if status == 'next_level':
                current_level += 1
                if current_level > 5:
                    game_outcome = 'win'
                    break # All levels beaten
                else:
                    # Display level complete message and prepare for next level
                    end_choice = end_screen(screen, clock, font, f"Level {current_level - 1} Complete! Score: {total_score}")
                    if end_choice == 'quit':
                        game_outcome = 'quit'
                        break
            elif status == 'game_over':
                game_outcome = 'game_over'
                break
            elif status == 'quit':
                game_outcome = 'quit'
                break
        
        scores.save_score("Breakout", total_score)

        if game_outcome == 'win':
            congratulations_screen(screen, clock, font, total_score)
        elif game_outcome == 'game_over':
            end_choice = end_screen(screen, clock, font, f"Game Over! Score: {total_score}")
            if end_choice == 'quit':
                return total_score
        elif game_outcome == 'quit':
            return total_score

if __name__ == "__main__":
    # This block runs when the script is executed directly.
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()