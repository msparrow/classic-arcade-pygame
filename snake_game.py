"""
Pygame implementation of the classic arcade game Snake.

This script contains the game logic for Snake, including player movement,
food consumption, and collision detection. It also features a start menu,
game over screen, and difficulty settings.
"""

import pygame
import sys
import random

# Import shared modules and constants.
from config import BLACK, WHITE, GREEN, RED, GRAY, DEFAULT_MUSIC_VOLUME
from utils import draw_text, pause_menu, settings_menu
import scores

# --- Initialization ---
# Initialize all imported Pygame modules.
pygame.init()

# --- Difficulty Settings ---
# A dictionary mapping difficulty levels to game speed.
DIFFICULTIES = {
    "Easy": 10,
    "Medium": 15,
    "Hard": 20
}

# --- Constants ---
# Screen dimensions.
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
# Cell size for the grid-based game.
CELL_SIZE = 20
# Grid dimensions derived from screen size and cell size.
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

# Game States
# Constants representing the different states of the game.
START_MENU = 0
PLAYING = 1
GAME_OVER = 2

def start_menu(screen, clock, font, small_font, current_difficulty):
    """
    Displays the start menu and handles its input.

    Args:
        screen (pygame.Surface): The screen to draw the menu on.
        clock (pygame.time.Clock): The Pygame clock object.
        font (pygame.font.Font): The font for the title.
        small_font (pygame.font.Font): The font for the buttons and other text.
        current_difficulty (str): The currently selected difficulty.

    Returns:
        tuple: A tuple containing the next game state and the selected difficulty.
    """
    # Colors for the start menu UI.
    BACKGROUND_COLOR = (10, 20, 10)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (0, 255, 0)
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    selected_difficulty = current_difficulty
    # Main loop for the start menu.
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("Snake Game", font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)

        mx, my = pygame.mouse.get_pos()

        # Difficulty selection UI.
        difficulty_text_y = SCREEN_HEIGHT / 2 - 60
        draw_text("Difficulty:", small_font, TEXT_COLOR, screen, SCREEN_WIDTH / 2, difficulty_text_y)
        
        difficulty_buttons = []
        button_width_diff = 100
        button_height_diff = 40
        button_spacing_diff = 20
        total_width_diff = len(DIFFICULTIES) * (button_width_diff + button_spacing_diff) - button_spacing_diff
        button_x_start_diff = SCREEN_WIDTH / 2 - total_width_diff / 2

        for i, (name, speed) in enumerate(DIFFICULTIES.items()):
            button_rect = pygame.Rect(button_x_start_diff + i * (button_width_diff + button_spacing_diff), difficulty_text_y + 40, button_width_diff, button_height_diff)
            difficulty_buttons.append({'rect': button_rect, 'name': name, 'speed': speed})
            
            color = HIGHLIGHT_COLOR if name == selected_difficulty else TEXT_COLOR
            current_button_color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mx, my) else BUTTON_COLOR
            pygame.draw.rect(screen, current_button_color, button_rect, border_radius=10)
            pygame.draw.rect(screen, BORDER_COLOR, button_rect, 2, border_radius=10)
            draw_text(name, small_font, color, screen, button_rect.centerx, button_rect.centery)

        # Main menu buttons (Start, Settings, Quit).
        button_width = 250
        button_height = 60
        button_spacing = 20

        settings_y = difficulty_text_y + 40 + button_height_diff + button_spacing * 2
        start_y = settings_y + button_height + button_spacing
        quit_y = start_y + button_height + button_spacing

        settings_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, settings_y, button_width, button_height)
        start_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, start_y, button_width, button_height)
        quit_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, quit_y, button_width, button_height)

        buttons = [
            {"text": "Settings", "rect": settings_button_rect, "action": "settings"},
            {"text": "Start Game", "rect": start_button_rect, "action": PLAYING},
            {"text": "Quit", "rect": quit_button_rect, "action": 'QUIT'}
        ]

        # Event handling for the start menu.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'QUIT', selected_difficulty
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in difficulty_buttons:
                    if btn['rect'].collidepoint(event.pos):
                        selected_difficulty = btn['name']
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        if button["action"] == "settings":
                            new_volume, status = settings_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT, pygame.mixer.music.get_volume())
                            if status == 'quit': return 'QUIT', selected_difficulty
                        else:
                            return button["action"], selected_difficulty

        # Draw main menu buttons with hover effects.
        for button in buttons:
            current_button_color = BUTTON_HOVER_COLOR if button["rect"].collidepoint(mx, my) else BUTTON_COLOR
            pygame.draw.rect(screen, current_button_color, button["rect"], border_radius=10)
            pygame.draw.rect(screen, BORDER_COLOR, button["rect"], 2, border_radius=10)
            draw_text(button["text"], small_font, TEXT_COLOR, screen, button["rect"].centerx, button["rect"].centery)

        pygame.display.update()
        clock.tick(15)

def game_over_menu(screen, clock, font, small_font, score):
    """
    Displays the game over screen and returns the user's choice.

    Args:
        screen (pygame.Surface): The screen to draw the menu on.
        clock (pygame.time.Clock): The Pygame clock object.
        font (pygame.font.Font): The font for the title.
        small_font (pygame.font.Font): The font for the buttons and score.
        score (int): The player's final score.

    Returns:
        str: The action selected by the user ('PLAYING' to restart, 'QUIT' to quit).
    """
    # Colors for the game over menu UI.
    BACKGROUND_COLOR = (10, 20, 10)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (255, 0, 0)
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    # Main loop for the game over menu.
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("Game Over", font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        draw_text(f"Final Score: {score}", small_font, TEXT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4 + 60)

        mx, my = pygame.mouse.get_pos()

        # Define button properties.
        button_width = 250
        button_height = 60
        button_spacing = 20

        restart_y = SCREEN_HEIGHT / 2 + 50
        quit_y = restart_y + button_height + button_spacing

        restart_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, restart_y, button_width, button_height)
        quit_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, quit_y, button_width, button_height)

        buttons = [
            {"text": "Restart", "rect": restart_button_rect, "action": PLAYING},
            {"text": "Quit", "rect": quit_button_rect, "action": 'QUIT'}
        ]

        # Event handling for the game over menu.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'QUIT'
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        return button["action"]

        # Draw buttons with hover effects.
        for button in buttons:
            current_button_color = BUTTON_HOVER_COLOR if button["rect"].collidepoint(mx, my) else BUTTON_COLOR
            pygame.draw.rect(screen, current_button_color, button["rect"], border_radius=10)
            pygame.draw.rect(screen, BORDER_COLOR, button["rect"], 2, border_radius=10)
            draw_text(button["text"], small_font, TEXT_COLOR, screen, button["rect"].centerx, button["rect"].centery)

        pygame.display.update()
        clock.tick(15)

def game_loop(screen, clock, small_font, game_speed):
    """
    The main loop for the Snake game itself.

    Args:
        screen (pygame.Surface): The screen to draw the game on.
        clock (pygame.time.Clock): The Pygame clock object.
        small_font (pygame.font.Font): The font for the score display.
        game_speed (int): The speed of the snake, controlled by the difficulty setting.

    Returns:
        tuple: A tuple containing the final score and the next game state.
    """
    # Initialize snake position and body.
    snake_pos = [GRID_WIDTH // 2, GRID_HEIGHT // 2]
    snake_body = [[snake_pos[0], snake_pos[1]], [snake_pos[0] - 1, snake_pos[1]], [snake_pos[0] - 2, snake_pos[1]]]
    direction = 'RIGHT'
    change_to = direction
    score = 0

    # Initialize food position.
    food_pos = [random.randrange(1, GRID_WIDTH), random.randrange(1, GRID_HEIGHT)]

    # Main game loop.
    while True:
        # Event handling.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score, GAME_OVER
            elif event.type == pygame.KEYDOWN:
                # Change snake direction based on key presses.
                if event.key in (pygame.K_UP, pygame.K_w) and direction != 'DOWN': change_to = 'UP'
                if event.key in (pygame.K_DOWN, pygame.K_s) and direction != 'UP': change_to = 'DOWN'
                if event.key in (pygame.K_LEFT, pygame.K_a) and direction != 'RIGHT': change_to = 'LEFT'
                if event.key in (pygame.K_RIGHT, pygame.K_d) and direction != 'LEFT': change_to = 'RIGHT'
                if event.key == pygame.K_p:
                    # Pause the game.
                    pause_choice = pause_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT)
                    if pause_choice == 'quit':
                        return score, GAME_OVER

        direction = change_to

        # Move the snake.
        if direction == 'UP': snake_pos[1] -= 1
        if direction == 'DOWN': snake_pos[1] += 1
        if direction == 'LEFT': snake_pos[0] -= 1
        if direction == 'RIGHT': snake_pos[0] += 1

        # Update snake body.
        snake_body.insert(0, list(snake_pos))
        # Check for food collision.
        if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
            score += 1
            # Generate new food.
            food_pos = [random.randrange(1, GRID_WIDTH), random.randrange(1, GRID_HEIGHT)]
        else:
            # Remove the last segment of the snake's body.
            snake_body.pop()

        # --- Drawing ---
        screen.fill(BLACK)
        # Draw the snake.
        for pos in snake_body:
            pygame.draw.rect(screen, GREEN, pygame.Rect(pos[0] * CELL_SIZE, pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        # Draw the food.
        pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0] * CELL_SIZE, food_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # --- Game Over Conditions ---
        # Check for collision with the screen boundaries.
        if not (0 <= snake_pos[0] < GRID_WIDTH and 0 <= snake_pos[1] < GRID_HEIGHT):
            return score, GAME_OVER
        # Check for collision with the snake's own body.
        for block in snake_body[1:]:
            if snake_pos == block:
                return score, GAME_OVER

        # Draw the score.
        draw_text(f"Score: {score}", small_font, WHITE, screen, 10, 10, center=False)

        pygame.display.update()
        clock.tick(game_speed)

def run_game(screen, clock):
    """
    Main function to manage the game states for Snake.

    Args:
        screen (pygame.Surface): The main screen surface.
        clock (pygame.time.Clock): The Pygame clock object.
    """
    pygame.display.set_caption("Snake Game")
    # Resize the screen for this game.
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 36)

    # Initialize game state variables.
    game_state = START_MENU
    score = 0
    current_difficulty = "Medium"
    game_speed = DIFFICULTIES[current_difficulty]

    # Main state machine loop.
    while True:
        if game_state == START_MENU:
            game_state, selected_difficulty = start_menu(screen, clock, font, small_font, current_difficulty)
            if game_state == 'QUIT': return 0
            current_difficulty = selected_difficulty
            game_speed = DIFFICULTIES[current_difficulty]
        elif game_state == PLAYING:
            score, game_state = game_loop(screen, clock, small_font, game_speed)
            scores.save_score("Snake", score)
        elif game_state == GAME_OVER:
            game_state = game_over_menu(screen, clock, font, small_font, score)
            if game_state == 'QUIT': return score

if __name__ == "__main__":
    # This block runs when the script is executed directly.
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()
