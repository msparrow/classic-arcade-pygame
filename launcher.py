"""
Main launcher for the Pygame Arcade.

This script initializes Pygame, displays a main menu with a list of available games,
and allows the user to select a game to play. It also provides access to a high scores screen
and a settings menu.

The launcher handles music, user input, and the overall game selection flow.
"""

import pygame
import sys

# Import shared modules
# These modules contain configuration variables, utility functions, and score handling.
from config import LAUNCHER_WIDTH, LAUNCHER_HEIGHT, BLACK, WHITE, GRAY, DEFAULT_MUSIC_VOLUME
from utils import draw_text, settings_menu
import scores

# Import the game modules
# Each game is in its own module and is imported here.
import snake_game
import pong
import space_invaders
import breakout
import asteroids
import tetris_game
import minesweeper
import pacman
import frogger
import galaga
import cyber_ninja
import beat_em_up
import tic_tac_toe

# --- Initialization ---
# Initialize all imported Pygame modules.
pygame.init()
# Initialize the mixer for sound playback.
pygame.mixer.init()

# --- Constants ---
# Define font sizes for the launcher UI.
FONT_SIZE = 40
TITLE_FONT_SIZE = 60

# --- Game Configuration ---
# A dictionary mapping the display name of each game to its corresponding module.
# This makes it easy to add or remove games from the launcher.
GAMES = {
    "Asteroids": asteroids,
    "Beat 'em Up": beat_em_up,
    "Breakout": breakout,
    "Cyber-Ninja Showdown": cyber_ninja,
    "Minesweeper": minesweeper,
    "Pac-Man": pacman,
    "Pong": pong,
    "Snake": snake_game,
    "Space Invaders": space_invaders,
    "Tetris": tetris_game,
    "Frogger": frogger,
    "Galaga": galaga,
    "Tic Tac Toe": tic_tac_toe,
}

def show_high_scores(screen, clock):
    """
    Displays the high scores for all games.

    This function creates a new screen to show the high scores, loaded from the scores module.
    It includes a back button to return to the main menu.

    Args:
        screen (pygame.Surface): The main screen surface to draw on.
        clock (pygame.time.Clock): The Pygame clock object for controlling the frame rate.
    """
    # Fonts for the high scores screen.
    title_font = pygame.font.Font(None, 80)
    score_font = pygame.font.Font(None, 40)
    button_font = pygame.font.Font(None, 40)

    # Colors for a visually appealing high scores screen.
    BACKGROUND_COLOR = (20, 20, 40) # Dark Blue/Purple
    TEXT_COLOR = (255, 255, 255) # White
    HIGHLIGHT_COLOR = (255, 215, 0) # Gold
    BUTTON_COLOR = (50, 50, 50) # Dark Gray
    BUTTON_HOVER_COLOR = (80, 80, 80) # Lighter Gray on hover
    BORDER_COLOR = (150, 150, 150) # Medium Gray
    
    # Load high scores and sort them in descending order.
    high_scores = scores.load_scores()
    sorted_scores = sorted(high_scores.items(), key=lambda item: item[1], reverse=True)

    # Main loop for the high scores screen.
    while True:
        # Fill the background.
        screen.fill(BACKGROUND_COLOR)
        # Draw the title.
        draw_text("High Scores", title_font, HIGHLIGHT_COLOR, screen, LAUNCHER_WIDTH / 2, 70)

        # Display the scores.
        y_offset = 150
        if not sorted_scores:
            draw_text("No scores yet! Play some games!", score_font, TEXT_COLOR, screen, LAUNCHER_WIDTH / 2, y_offset + 50)
        else:
            # Display the top 10 scores.
            for i, (game, score) in enumerate(sorted_scores[:10]):
                color = TEXT_COLOR
                # Highlight the top score.
                if i == 0:
                    color = HIGHLIGHT_COLOR
                draw_text(f"{game}: {score}", score_font, color, screen, LAUNCHER_WIDTH / 2, y_offset)
                y_offset += 50

        # Back button to return to the main menu.
        back_button_rect = pygame.Rect(LAUNCHER_WIDTH / 2 - 125, LAUNCHER_HEIGHT - 70, 250, 60)
        mx, my = pygame.mouse.get_pos()
        current_button_color = BUTTON_HOVER_COLOR if back_button_rect.collidepoint((mx, my)) else BUTTON_COLOR
        
        pygame.draw.rect(screen, current_button_color, back_button_rect, border_radius=10)
        pygame.draw.rect(screen, BORDER_COLOR, back_button_rect, 2, border_radius=10)
        draw_text("Back", button_font, TEXT_COLOR, screen, back_button_rect.centerx, back_button_rect.centery)

        # Event handling for the high scores screen.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button_rect.collidepoint(event.pos):
                    return # Exit the high scores screen.

        # Update the display and control the frame rate.
        pygame.display.flip()
        clock.tick(30)

def main_menu(screen, clock):
    """
    Displays the main game selection menu.

    This function handles the main loop of the launcher, including drawing the menu,
    handling user input, and launching the selected game.

    Args:
        screen (pygame.Surface): The main screen surface to draw on.
        clock (pygame.time.Clock): The Pygame clock object for controlling the frame rate.
    """
    # Fonts for the main menu.
    title_font = pygame.font.Font(None, 90)
    button_font = pygame.font.Font(None, 45)

    # Colors for a visually appealing main menu.
    BACKGROUND_COLOR = (20, 20, 40) # Dark Blue/Purple
    TEXT_COLOR = (255, 255, 255) # White
    HIGHLIGHT_COLOR = (255, 215, 0) # Gold
    BUTTON_COLOR = (50, 50, 50) # Dark Gray
    BUTTON_HOVER_COLOR = (80, 80, 80) # Lighter Gray on hover
    BORDER_COLOR = (150, 150, 150) # Medium Gray

    # Initialize music volume.
    current_music_volume = DEFAULT_MUSIC_VOLUME
    
    # Create a list of buttons for the game menu.
    buttons = []
    start_y = 180 # Starting Y position for the first button.
    for i, (game_name, module) in enumerate(GAMES.items()):
        buttons.append({'text': game_name, 'module': module})

    # Variables for scrolling the menu.
    scroll_offset = 0
    button_spacing = 70 # Spacing between buttons.

    # Calculate the maximum scroll offset to prevent scrolling past the last button.
    total_buttons_height = len(buttons) * button_spacing
    max_scroll = max(0, total_buttons_height - (LAUNCHER_HEIGHT - start_y - 150))

    # Main loop for the main menu.
    while True:
        # Fill the background.
        screen.fill(BACKGROUND_COLOR)
        # Draw the title.
        draw_text("Pygame Arcade", title_font, HIGHLIGHT_COLOR, screen, LAUNCHER_WIDTH / 2, 90)
        
        # Get the current mouse position.
        mx, my = pygame.mouse.get_pos()

        # Draw the game selection buttons.
        for i, button in enumerate(buttons):
            y_pos = start_y + (i * button_spacing) - scroll_offset
            button_rect = pygame.Rect(LAUNCHER_WIDTH / 2 - 175, y_pos, 350, 60)
            button['rect'] = button_rect # Store the rect for collision detection.

            # Only draw the button if it is within the visible area of the screen.
            if y_pos < LAUNCHER_HEIGHT and y_pos + button_rect.height > 0:
                color = BUTTON_HOVER_COLOR if button_rect.collidepoint((mx, my)) else BUTTON_COLOR
                pygame.draw.rect(screen, color, button_rect, border_radius=15)
                pygame.draw.rect(screen, BORDER_COLOR, button_rect, 2, border_radius=15)
                draw_text(button['text'], button_font, TEXT_COLOR, screen, button_rect.centerx, button_rect.centery)

        # Draw the High Scores button.
        high_scores_button_rect = pygame.Rect(30, LAUNCHER_HEIGHT - 70, 200, 50)
        high_scores_button_color = BUTTON_HOVER_COLOR if high_scores_button_rect.collidepoint((mx, my)) else BUTTON_COLOR
        pygame.draw.rect(screen, high_scores_button_color, high_scores_button_rect, border_radius=10)
        pygame.draw.rect(screen, BORDER_COLOR, high_scores_button_rect, 2, border_radius=10)
        draw_text("High Scores", button_font, TEXT_COLOR, screen, high_scores_button_rect.centerx, high_scores_button_rect.centery)

        # Draw the Settings button.
        settings_button_rect = pygame.Rect(LAUNCHER_WIDTH - 230, LAUNCHER_HEIGHT - 70, 200, 50)
        settings_button_color = BUTTON_HOVER_COLOR if settings_button_rect.collidepoint((mx, my)) else BUTTON_COLOR
        pygame.draw.rect(screen, settings_button_color, settings_button_rect, border_radius=10)
        pygame.draw.rect(screen, BORDER_COLOR, settings_button_rect, 2, border_radius=10)
        draw_text("Settings", button_font, TEXT_COLOR, screen, settings_button_rect.centerx, settings_button_rect.centery)

        # Event handling for the main menu.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if a game button was clicked.
                for button in buttons:
                    if button.get('rect') and button['rect'].collidepoint(event.pos):
                        # Run the selected game.
                        button['module'].run_game(screen, clock)
                        # Reset the screen and caption for the launcher.
                        pygame.display.set_caption("Pygame Arcade")
                        screen = pygame.display.set_mode((LAUNCHER_WIDTH, LAUNCHER_HEIGHT))
                        # Re-apply launcher music settings after returning from a game.
                        pygame.mixer.music.set_volume(current_music_volume)
                        pygame.mixer.music.play(-1)

                # Check if the High Scores button was clicked.
                if high_scores_button_rect.collidepoint(event.pos):
                    show_high_scores(screen, clock)

                # Check if the Settings button was clicked.
                if settings_button_rect.collidepoint(event.pos):
                    new_volume, status = settings_menu(screen, clock, LAUNCHER_WIDTH, LAUNCHER_HEIGHT, current_music_volume)
                    current_music_volume = new_volume
                    pygame.mixer.music.set_volume(current_music_volume)
                    if status == 'quit':
                        return # Exit the launcher.

            # Handle mouse wheel scrolling for the game menu.
            if event.type == pygame.MOUSEWHEEL:
                scroll_offset -= event.y * 30
                # Clamp the scroll offset to the valid range.
                scroll_offset = max(0, min(scroll_offset, max_scroll))

        # Update the display and control the frame rate.
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    # This block runs when the script is executed directly.
    
    # Load and play the menu music.
    try:
        pygame.mixer.music.load('assets/music/menu_theme.wav')
        pygame.mixer.music.play(-1) # Loop the music indefinitely.
        pygame.mixer.music.set_volume(DEFAULT_MUSIC_VOLUME)
    except pygame.error:
        print("Could not load menu music. Make sure 'assets/music/menu_theme.wav' exists.")

    # Set up the display screen and caption.
    screen = pygame.display.set_mode((LAUNCHER_WIDTH, LAUNCHER_HEIGHT))
    pygame.display.set_caption("Pygame Arcade")
    # Create a clock object to control the frame rate.
    clock = pygame.time.Clock()
    # Start the main menu.
    main_menu(screen, clock)
    # Quit Pygame and exit the program when the main menu loop finishes.
    pygame.quit()
    sys.exit()

# Add a placeholder get_instructions function if needed by other modules.
# This can be useful for maintaining a consistent interface across all game modules.
def get_instructions():
    """
    Returns a list of instructions for the launcher.
    """
    return ["Select a game from the menu."]
