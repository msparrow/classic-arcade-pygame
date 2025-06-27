import pygame
import sys

# Import shared modules
from config import LAUNCHER_WIDTH, LAUNCHER_HEIGHT, BLACK, WHITE, GRAY
from utils import draw_text

# Import the game modules
import snake_game
import pong
import space_invaders
import breakout
import asteroids
import tetris_game
import minesweeper

# --- Initialization ---
pygame.init()

# --- Constants ---
FONT_SIZE = 40
TITLE_FONT_SIZE = 60

# --- Game Configuration ---
GAMES = {
    "Asteroids": asteroids,
    "Breakout": breakout,
    "Minesweeper": minesweeper,
    "Pong": pong,
    "Snake": snake_game,
    "Space Invaders": space_invaders,
    "Tetris": tetris_game,
}

def main_menu(screen, clock):
    """Displays the main game selection menu."""
    title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
    button_font = pygame.font.Font(None, FONT_SIZE)
    
    buttons = []
    start_y = 150
    for i, game_name in enumerate(GAMES.keys()):
        y_pos = start_y + i * (FONT_SIZE + 20)
        button_rect = pygame.Rect(LAUNCHER_WIDTH / 2 - 150, y_pos, 300, FONT_SIZE + 10)
        buttons.append({'rect': button_rect, 'text': game_name, 'module': GAMES[game_name]})

    while True:
        screen.fill(BLACK)
        draw_text("Pygame Arcade", title_font, WHITE, screen, LAUNCHER_WIDTH / 2, 70)

        mx, my = pygame.mouse.get_pos()

        for button in buttons:
            color = GRAY if not button['rect'].collidepoint((mx, my)) else WHITE
            pygame.draw.rect(screen, color, button['rect'], 2)
            draw_text(button['text'], button_font, WHITE, screen, button['rect'].centerx, button['rect'].centery)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button['rect'].collidepoint(event.pos):
                        button['module'].run_game(screen, clock)
                        pygame.display.set_caption("Pygame Arcade") # Reset caption
                        screen = pygame.display.set_mode((LAUNCHER_WIDTH, LAUNCHER_HEIGHT)) # Reset screen size for launcher
                        
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    screen = pygame.display.set_mode((LAUNCHER_WIDTH, LAUNCHER_HEIGHT))
    pygame.display.set_caption("Pygame Arcade")
    clock = pygame.time.Clock()
    main_menu(screen, clock)
    pygame.quit()
    sys.exit()