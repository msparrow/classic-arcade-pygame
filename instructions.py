"""
This module handles the display of game-specific instructions.
"""

import pygame

# Import shared modules and constants.
from config import BLACK, WHITE, LAUNCHER_WIDTH, LAUNCHER_HEIGHT
from utils import draw_text

def show_instructions(screen, clock, game_name, instructions_list):
    """
    Displays a screen with game-specific instructions.

    Args:
        screen (pygame.Surface): The screen to draw the instructions on.
        clock (pygame.time.Clock): The Pygame clock object.
        game_name (str): The name of the game.
        instructions_list (list): A list of strings, where each string is a line of instruction.

    Returns:
        str: 'continue' if the user proceeds, 'quit' if the user closes the window.
    """
    # Fonts for the instructions screen.
    title_font = pygame.font.Font(None, 60)
    instruction_font = pygame.font.Font(None, 30)
    small_font = pygame.font.Font(None, 24)

    # Main loop for the instructions screen.
    running = True
    while running:
        screen.fill(BLACK)
        # Draw the title.
        draw_text(f"{game_name} Instructions", title_font, WHITE, screen, LAUNCHER_WIDTH / 2, 50)

        # Draw the instruction lines.
        y_offset = 120
        for line in instructions_list:
            draw_text(line, instruction_font, WHITE, screen, LAUNCHER_WIDTH / 2, y_offset)
            y_offset += 40

        # Prompt the user to continue.
        draw_text("Press any key or click to continue...", small_font, WHITE, screen, LAUNCHER_WIDTH / 2, LAUNCHER_HEIGHT - 50)

        # Event handling.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                running = False

        pygame.display.flip()
        clock.tick(30)
    return 'continue'
