"""
Pygame implementation of the classic arcade game Frogger.
"""

import pygame
import sys
import random

from config import BLACK, WHITE, GREEN, GRAY, BLUE, RED
from utils import draw_text, pause_menu, settings_menu
import scores

# --- Initialization ---
pygame.init()

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FROG_SIZE = 40

# Lane properties
LANE_HEIGHT = 50
NUM_ROAD_LANES = 5
NUM_RIVER_LANES = 5

# Y-coordinates for different sections
SAFE_ZONE_TOP = SCREEN_HEIGHT - LANE_HEIGHT # Starting safe zone
ROAD_TOP = SAFE_ZONE_TOP - (LANE_HEIGHT * NUM_ROAD_LANES)
RIVER_TOP = ROAD_TOP - (LANE_HEIGHT * NUM_RIVER_LANES)
HOME_ROW_TOP = RIVER_TOP - LANE_HEIGHT # Final safe zone

# Speeds
CAR_SPEED_MIN, CAR_SPEED_MAX = 3, 7
LOG_SPEED_MIN, LOG_SPEED_MAX = 2, 5
FROG_SPEED = LANE_HEIGHT # Frog moves one lane at a time

# Colors
ROAD_COLOR = GRAY
RIVER_COLOR = BLUE
SAFE_COLOR = GREEN
CAR_COLOR = RED
LOG_COLOR = (139, 69, 19) # Brown

class Frog:
    def __init__(self):
        self.reset()
        self.lives = 3

    def reset(self):
        self.x = SCREEN_WIDTH // 2 - FROG_SIZE // 2
        self.y = SAFE_ZONE_TOP + (LANE_HEIGHT - FROG_SIZE) // 2
        self.rect = pygame.Rect(self.x, self.y, FROG_SIZE, FROG_SIZE)
        self.on_log = False

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)
        # Keep frog within horizontal bounds
        if self.x < 0: self.x = 0
        if self.x > SCREEN_WIDTH - FROG_SIZE: self.x = SCREEN_WIDTH - FROG_SIZE

    def draw(self, screen):
        # Body
        pygame.draw.ellipse(screen, GREEN, self.rect)
        # Eyes
        eye_radius = FROG_SIZE // 6
        eye_offset = FROG_SIZE // 4
        pygame.draw.circle(screen, WHITE, (self.rect.centerx - eye_offset, self.rect.top + eye_offset), eye_radius)
        pygame.draw.circle(screen, WHITE, (self.rect.centerx + eye_offset, self.rect.top + eye_offset), eye_radius)
        pygame.draw.circle(screen, BLACK, (self.rect.centerx - eye_offset, self.rect.top + eye_offset), eye_radius // 2)
        pygame.draw.circle(screen, BLACK, (self.rect.centerx + eye_offset, self.rect.top + eye_offset), eye_radius // 2)

class Car:
    def __init__(self, x, y, speed, direction):
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = direction # 1 for right, -1 for left
        self.width = random.randint(50, 100)
        self.rect = pygame.Rect(self.x, self.y, self.width, FROG_SIZE)

    def update(self):
        self.x += self.speed * self.direction
        if self.direction == 1 and self.x > SCREEN_WIDTH: # Moving right, off screen
            self.x = -self.width
        elif self.direction == -1 and self.x < -self.width: # Moving left, off screen
            self.x = SCREEN_WIDTH
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        # Main body of the car
        pygame.draw.rect(screen, CAR_COLOR, self.rect)
        # Roof/Cabin
        pygame.draw.rect(screen, (CAR_COLOR[0] - 50, CAR_COLOR[1] - 50, CAR_COLOR[2] - 50), 
                         (self.rect.x + self.rect.width * 0.2, self.rect.y, self.rect.width * 0.6, self.rect.height * 0.6))
        # Headlights
        pygame.draw.rect(screen, WHITE, (self.rect.x + 2, self.rect.y + self.rect.height - 5, 5, 3))
        pygame.draw.rect(screen, WHITE, (self.rect.x + self.rect.width - 7, self.rect.y + self.rect.height - 5, 5, 3))

class Log:
    def __init__(self, x, y, speed, direction):
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = direction
        self.width = random.randint(80, 150)
        self.rect = pygame.Rect(self.x, self.y, self.width, FROG_SIZE)

    def update(self):
        self.x += self.speed * self.direction
        if self.direction == 1 and self.x > SCREEN_WIDTH: # Moving right, off screen
            self.x = -self.width
        elif self.direction == -1 and self.x < -self.width: # Moving left, off screen
            self.x = SCREEN_WIDTH
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        # Main body of the log
        pygame.draw.rect(screen, LOG_COLOR, self.rect)
        # Add some lines to simulate wood grain
        for i in range(1, 4):
            pygame.draw.line(screen, (LOG_COLOR[0] - 20, LOG_COLOR[1] - 20, LOG_COLOR[2] - 20),
                             (self.rect.x, self.rect.y + i * (self.rect.height // 4)),
                             (self.rect.x + self.rect.width, self.rect.y + i * (self.rect.height // 4)), 2)

def main_menu(screen, clock, font, small_font):
    """Displays the main menu for Frogger."""
    # Colors
    BACKGROUND_COLOR = (10, 30, 10) # Darker green
    TEXT_COLOR = (255, 255, 255) # White
    HIGHLIGHT_COLOR = (0, 255, 0) # Green
    BUTTON_COLOR = (50, 50, 50) # Dark Gray
    BUTTON_HOVER_COLOR = (80, 80, 80) # Lighter Gray on hover
    BORDER_COLOR = (150, 150, 150) # Medium Gray

    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("Frogger", font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        
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

def game_loop(screen, clock, font, level):
    pygame.display.set_caption(f"Frogger - Level {level}")
    frog = Frog()
    score = 0
    
    # Generate cars and logs based on level
    cars = []
    for i in range(NUM_ROAD_LANES):
        y = ROAD_TOP + i * LANE_HEIGHT + (LANE_HEIGHT - FROG_SIZE) // 2
        num_cars = 2 + level // 2 # More cars on higher levels
        for _ in range(num_cars):
            speed = random.randint(CAR_SPEED_MIN + level, CAR_SPEED_MAX + level)
            direction = 1 if i % 2 == 0 else -1 # Alternate direction
            x = random.randint(0, SCREEN_WIDTH)
            cars.append(Car(x, y, speed, direction))

    logs = []
    for i in range(NUM_RIVER_LANES):
        y = RIVER_TOP + i * LANE_HEIGHT + (LANE_HEIGHT - FROG_SIZE) // 2
        num_logs = 2 + level // 2 # More logs on higher levels
        for _ in range(num_logs):
            speed = random.randint(LOG_SPEED_MIN + level, LOG_SPEED_MAX + level)
            direction = 1 if i % 2 == 1 else -1 # Alternate direction
            x = random.randint(0, SCREEN_WIDTH)
            logs.append(Log(x, y, speed, direction))

    # Home positions for frogs to reach
    home_positions = []
    for i in range(5): # 5 home spots
        home_positions.append(pygame.Rect(50 + i * 150, HOME_ROW_TOP, FROG_SIZE, FROG_SIZE))
    occupied_homes = [False] * 5

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score, 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: frog.move(0, -FROG_SPEED)
                elif event.key == pygame.K_DOWN: frog.move(0, FROG_SPEED)
                elif event.key == pygame.K_LEFT: frog.move(-FROG_SPEED, 0)
                elif event.key == pygame.K_RIGHT: frog.move(FROG_SPEED, 0)
                elif event.key == pygame.K_p:
                    pause_choice = pause_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT)
                    if pause_choice == 'quit': return score, 'quit'

        # Update cars and logs
        for car in cars: car.update()
        for log in logs: log.update()

        # Frog on log logic
        frog.on_log = False
        if RIVER_TOP <= frog.y < ROAD_TOP: # If in river section
            for log in logs:
                if frog.rect.colliderect(log.rect):
                    frog.x += log.speed * log.direction
                    frog.on_log = True
                    break
            if not frog.on_log: # If in water and not on a log
                frog.lives -= 1
                if frog.lives <= 0: return score, 'game_over'
                frog.reset()

        # Collision with cars
        if ROAD_TOP <= frog.y < SAFE_ZONE_TOP:
            for car in cars:
                if frog.rect.colliderect(car.rect):
                    frog.lives -= 1
                    if frog.lives <= 0: return score, 'game_over'
                    frog.reset()

        # Check if frog reached home
        if frog.y < RIVER_TOP:
            home_reached = False
            for i, home_rect in enumerate(home_positions):
                if frog.rect.colliderect(home_rect) and not occupied_homes[i]:
                    occupied_homes[i] = True
                    score += 100 # Score for reaching home
                    frog.reset()
                    home_reached = True
                    break
            if not home_reached: # Fell into water at home row or hit occupied home
                frog.lives -= 1
                if frog.lives <= 0: return score, 'game_over'
                frog.reset()

        # Check if all homes are occupied (level complete)
        if all(occupied_homes):
            return score, 'next_level'

        # Drawing
        screen.fill(BLACK)

        # Draw safe zones
        pygame.draw.rect(screen, SAFE_COLOR, (0, SAFE_ZONE_TOP, SCREEN_WIDTH, LANE_HEIGHT))
        pygame.draw.rect(screen, SAFE_COLOR, (0, HOME_ROW_TOP, SCREEN_WIDTH, LANE_HEIGHT))

        # Draw road lanes
        for i in range(NUM_ROAD_LANES):
            y = ROAD_TOP + i * LANE_HEIGHT
            pygame.draw.rect(screen, ROAD_COLOR, (0, y, SCREEN_WIDTH, LANE_HEIGHT))

        # Draw river lanes
        for i in range(NUM_RIVER_LANES):
            y = RIVER_TOP + i * LANE_HEIGHT
            pygame.draw.rect(screen, RIVER_COLOR, (0, y, SCREEN_WIDTH, LANE_HEIGHT))

        for car in cars: car.draw(screen)
        for log in logs: log.draw(screen)
        frog.draw(screen)

        # Draw UI
        draw_text(f"Score: {score}", font, WHITE, screen, 100, 20)
        draw_text(f"Lives: {frog.lives}", font, WHITE, screen, SCREEN_WIDTH - 100, 20)
        draw_text(f"Level: {level}", font, WHITE, screen, SCREEN_WIDTH / 2, 20)

        pygame.display.flip()
        clock.tick(30)

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
    BACKGROUND_COLOR = (10, 30, 10)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (0, 255, 0) # Green
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    title_font = pygame.font.Font(None, 70)
    score_font = pygame.font.Font(None, 50)
    button_font = pygame.font.Font(None, 40)

    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("CONGRATULATIONS!", title_font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3 - 50)
        draw_text(f"You beat Frogger!", score_font, TEXT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3 + 20)
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
    BACKGROUND_COLOR = (10, 30, 10)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (0, 255, 0) # Green
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

def run_game(screen, clock):
    """
    Main function to manage the game states for Frogger.

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

        while current_level <= 5:
            level_score, status = game_loop(screen, clock, small_font, current_level)
            total_score += level_score # Accumulate score across levels

            if status == 'next_level':
                current_level += 1
                if current_level > 5:
                    game_outcome = 'win'
                    break
                else:
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

        scores.save_score("Frogger", total_score)

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