import pygame
import sys
import random

# Import shared modules
from config import BLACK, WHITE, GREEN, RED
from utils import draw_text

# --- Initialization ---
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
CELL_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

# Game States
START_MENU = 0
PLAYING = 1
GAME_OVER = 2

def start_menu(screen, clock, font, small_font):
    """Displays the start menu and handles its input."""
    while True:
        screen.fill(BLACK)
        draw_text("Snake Game", font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)

        start_button = draw_text("Start Game", small_font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        quit_button = draw_text("Quit", small_font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'QUIT'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return PLAYING
                if quit_button.collidepoint(event.pos):
                    return 'QUIT'

        pygame.display.update()
        clock.tick(15)

def game_over_menu(screen, clock, font, small_font, score):
    """Displays the game over screen and returns user choice."""
    while True:
        screen.fill(BLACK)
        draw_text("Game Over", font, RED, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        draw_text(f"Final Score: {score}", small_font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4 + 60)

        restart_button = draw_text("Restart", small_font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)
        quit_button = draw_text("Quit", small_font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'QUIT'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    return PLAYING
                if quit_button.collidepoint(event.pos):
                    return 'QUIT'

        pygame.display.update()
        clock.tick(15)

def game_loop(screen, clock, small_font):
    """The main loop for the game itself."""
    snake_pos = [GRID_WIDTH // 2, GRID_HEIGHT // 2] # x, y
    snake_body = [[snake_pos[0], snake_pos[1]], [snake_pos[0] - 1, snake_pos[1]], [snake_pos[0] - 2, snake_pos[1]]]
    direction = 'RIGHT'
    change_to = direction
    score = 0

    food_pos = [random.randrange(1, GRID_WIDTH), random.randrange(1, GRID_HEIGHT)]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Allows quitting from the game window
                return score, GAME_OVER # Treat closing window as game over
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w) and direction != 'DOWN': change_to = 'UP'
                if event.key in (pygame.K_DOWN, pygame.K_s) and direction != 'UP': change_to = 'DOWN'
                if event.key in (pygame.K_LEFT, pygame.K_a) and direction != 'RIGHT': change_to = 'LEFT'
                if event.key in (pygame.K_RIGHT, pygame.K_d) and direction != 'LEFT': change_to = 'RIGHT'

        direction = change_to

        if direction == 'UP': snake_pos[1] -= 1
        if direction == 'DOWN': snake_pos[1] += 1
        if direction == 'LEFT': snake_pos[0] -= 1
        if direction == 'RIGHT': snake_pos[0] += 1

        snake_body.insert(0, list(snake_pos))
        if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
            score += 1
            food_pos = [random.randrange(1, GRID_WIDTH), random.randrange(1, GRID_HEIGHT)]
        else:
            snake_body.pop()

        # --- Drawing ---
        screen.fill(BLACK)
        for pos in snake_body:
            pygame.draw.rect(screen, GREEN, pygame.Rect(pos[0] * CELL_SIZE, pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0] * CELL_SIZE, food_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # --- Game Over Conditions ---
        if not (0 <= snake_pos[0] < GRID_WIDTH and 0 <= snake_pos[1] < GRID_HEIGHT):
            return score, GAME_OVER
        for block in snake_body[1:]:
            if snake_pos == block:
                return score, GAME_OVER

        draw_text(f"Score: {score}", small_font, WHITE, screen, 10, 10, center=False)

        pygame.display.update()
        clock.tick(15)

def run_game(screen, clock):
    """Main function to manage game states."""
    pygame.display.set_caption("Snake Game")
    # Resize screen for this game
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.Font(None, 50)
    small_font = pygame.font.Font(None, 36)

    game_state = START_MENU
    score = 0

    while True:
        if game_state == START_MENU:
            game_state = start_menu(screen, clock, font, small_font)
            if game_state == 'QUIT': return
        elif game_state == PLAYING:
            score, game_state = game_loop(screen, clock, small_font)
        elif game_state == GAME_OVER:
            game_state = game_over_menu(screen, clock, font, small_font, score)
            if game_state == 'QUIT': return

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()