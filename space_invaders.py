"""
Pygame implementation of the classic arcade game Space Invaders.

This script contains the game logic for Space Invaders, including player movement,
- shooting, alien movement, and collision detection.
"""

import pygame
import sys
import random

# Import shared modules and constants.
from config import BLACK, WHITE, GREEN, RED
from utils import draw_text, pause_menu, settings_menu, create_explosion
import scores

# --- Initialization ---
# Initialize all imported Pygame modules.
pygame.init()

# --- Constants ---
# Screen dimensions.
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Player properties.
PLAYER_SIZE, PLAYER_SPEED = 50, 5

# Bullet properties.
BULLET_WIDTH, BULLET_HEIGHT, BULLET_SPEED = 5, 15, 10

# Alien properties.
ALIEN_ROWS, ALIEN_COLS = 5, 11
ALIEN_SIZE, ALIEN_GAP = 40, 10
ALIEN_SPEED_X, ALIEN_SPEED_Y = 1, 20
ALIEN_FIRE_RATE = 100  # Lower is faster.

def create_aliens():
    """
    Creates the initial grid of aliens.

    Returns:
        list: A list of pygame.Rect objects representing the aliens.
    """
    aliens = []
    for row in range(ALIEN_ROWS):
        for col in range(ALIEN_COLS):
            x = col * (ALIEN_SIZE + ALIEN_GAP) + 50
            y = row * (ALIEN_SIZE + ALIEN_GAP) + 50
            aliens.append(pygame.Rect(x, y, ALIEN_SIZE, ALIEN_SIZE))
    return aliens

def main_menu(screen, clock, font, small_font):
    """
    Displays the main menu for Space Invaders.

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
        draw_text("Space Invaders", font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)

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
        pygame.draw.circle(screen, (200, 200, 200), (int(star['x']), int(star['y'])), 1)

def game_loop(screen, clock, font, level, total_score=0):
    pygame.display.set_caption(f"Space Invaders - Level {level}")
    font = pygame.font.Font(None, 36)

    # Adjust alien properties based on level
    current_alien_speed_x = ALIEN_SPEED_X + (level - 1) * 0.5
    current_alien_speed_y = ALIEN_SPEED_Y + (level - 1) * 5
    current_alien_fire_rate = max(20, ALIEN_FIRE_RATE - (level - 1) * 10) # Lower is faster

    # Initialize game state.
    player = pygame.Rect(SCREEN_WIDTH / 2 - PLAYER_SIZE / 2, SCREEN_HEIGHT - 70, PLAYER_SIZE, PLAYER_SIZE)
    player_bullets, aliens, alien_bullets = [], create_aliens(), []
    alien_direction, score, lives = 1, total_score, 3
    particles = []
    stars = create_starfield(100)
    alien_animation_timer = 0

    # Main game loop.
    while True:
        # Event handling.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score, 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and len(player_bullets) < 3:
                    # Fire a bullet.
                    bullet = pygame.Rect(player.centerx - BULLET_WIDTH / 2, player.top, BULLET_WIDTH, BULLET_HEIGHT)
                    player_bullets.append(bullet)
                if event.key == pygame.K_p:
                    # Pause the game.
                    pause_choice = pause_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT)
                    if pause_choice == 'quit':
                        return score, 'quit'

        # Player movement.
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0: player.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and player.right < SCREEN_WIDTH: player.x += PLAYER_SPEED

        # Move player bullets.
        for bullet in player_bullets[:]:
            bullet.y -= BULLET_SPEED
            if bullet.bottom < 0:
                player_bullets.remove(bullet)

        # Move alien bullets.
        for bullet in alien_bullets[:]:
            bullet.y += BULLET_SPEED
            if bullet.top > SCREEN_HEIGHT:
                alien_bullets.remove(bullet)

        # Move aliens.
        move_down = False
        for alien in aliens:
            alien.x += alien_direction * current_alien_speed_x
            if alien.right >= SCREEN_WIDTH or alien.left <= 0:
                move_down = True
        if move_down:
            alien_direction *= -1
            for alien in aliens:
                alien.y += current_alien_speed_y
        
        alien_animation_timer += 1

        # Alien firing.
        if random.randint(1, current_alien_fire_rate) == 1 and aliens:
            shooter = random.choice(aliens)
            bullet = pygame.Rect(shooter.centerx - BULLET_WIDTH / 2, shooter.bottom, BULLET_WIDTH, BULLET_HEIGHT)
            alien_bullets.append(bullet)

        # Collision detection: player bullets and aliens.
        for bullet in player_bullets[:]:
            for alien in aliens[:]:
                if bullet.colliderect(alien):
                    player_bullets.remove(bullet)
                    aliens.remove(alien)
                    score += 100
                    create_explosion(particles, alien.centerx, alien.centery, RED)
                    break

        # Collision detection: alien bullets and player.
        for bullet in alien_bullets[:]:
            if bullet.colliderect(player):
                alien_bullets.remove(bullet)
                lives -= 1
                create_explosion(particles, player.centerx, player.centery, GREEN)
                if lives <= 0:
                    return score, 'game_over'

        # Check for win condition.
        if not aliens:
            return score, 'next_level'

        # Check for game over condition (aliens reached the bottom).
        for alien in aliens:
            if alien.bottom >= player.top:
                return score, 'game_over'

        # Update particles
        for p in particles:
            p.update()
        particles = [p for p in particles if p.life > 0]

        # Drawing everything.
        screen.fill(BLACK)
        draw_starfield(screen, stars)
        
        # Draw detailed player
        pygame.draw.rect(screen, GREEN, player, border_radius=5)
        pygame.draw.rect(screen, WHITE, (player.centerx - 5, player.top + 10, 10, 10))

        # Draw detailed aliens
        for alien in aliens:
            # Simple animation
            offset_y = 0
            if (alien_animation_timer // 30) % 2 == 0:
                offset_y = 5
            
            color = (200, 50, 50)
            pygame.draw.rect(screen, color, alien.move(0, offset_y), border_radius=5)
            pygame.draw.circle(screen, WHITE, (alien.centerx - 10, alien.centery - 5 + offset_y), 4)
            pygame.draw.circle(screen, WHITE, (alien.centerx + 10, alien.centery - 5 + offset_y), 4)

        for bullet in player_bullets:
            pygame.draw.rect(screen, (100, 255, 100), bullet)
        for bullet in alien_bullets:
            pygame.draw.rect(screen, (255, 100, 100), bullet)

        for p in particles:
            p.draw(screen)

        # Draw score and lives.
        draw_text(f"Score: {score}", font, WHITE, screen, 100, 20)
        draw_text(f"Lives: {lives}", font, WHITE, screen, SCREEN_WIDTH - 100, 20)
        draw_text(f"Level: {level}", font, WHITE, screen, SCREEN_WIDTH / 2, 20)

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
    while True:
        screen.fill(BLACK)
        draw_text(message, pygame.font.Font(None, 50), WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
        play_again_button = draw_text("Play Again", font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        quit_button = draw_text("Back to Menu", font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_button.collidepoint(event.pos):
                    return 'play_again'
                if quit_button.collidepoint(event.pos):
                    return 'quit'

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
    BACKGROUND_COLOR = (10, 10, 30)
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
        draw_text(f"You beat Space Invaders!", score_font, TEXT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3 + 20)
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
    Main function to manage the game states for Space Invaders.

    Args:
        screen (pygame.Surface): The main screen surface to draw on.
        clock (pygame.time.Clock): The Pygame clock object for controlling the frame rate.

    Returns:
        int: The final score of the player.
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
        
        scores.save_score("Space Invaders", total_score)

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