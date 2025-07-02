"""
Pygame implementation of the classic arcade game Tetris.

This script contains the game logic for Tetris, including the game board, tetrominoes,
- movement, rotation, line clearing, and scoring.
"""

import pygame
import sys
import random

# Import shared modules and constants.
from config import BLACK, WHITE, GRAY, DEFAULT_MUSIC_VOLUME
from utils import draw_text, pause_menu, settings_menu
import scores

# --- Initialization ---
# Initialize all imported Pygame modules.
pygame.init()

# --- Game Constants ---
# Grid dimensions.
COLS, ROWS = 10, 20
# Cell size.
CELL_SIZE = 30
# Game window dimensions.
GAME_WIDTH, GAME_HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE
SIDE_PANEL_WIDTH = 150
WINDOW_WIDTH, WINDOW_HEIGHT = GAME_WIDTH + SIDE_PANEL_WIDTH, GAME_HEIGHT
# Color for the grid lines.
GRID_COLOR = (80, 80, 80)

# Scoring based on the number of lines cleared at once.
SCORE_MAP = {1: 40, 2: 100, 3: 300, 4: 1200}

# --- Tetromino Shapes and Colors ---
# A dictionary defining the shapes and colors of the tetrominoes.
TETROMINOES = {
    'I': {'shape': [(0, -1), (0, 0), (0, 1), (0, 2)], 'color': (0, 255, 255)},
    'O': {'shape': [(0, 0), (1, 0), (0, 1), (1, 1)], 'color': (255, 255, 0)},
    'T': {'shape': [(-1, 0), (0, 0), (1, 0), (0, 1)], 'color': (128, 0, 128)},
    'S': {'shape': [(-1, 1), (0, 1), (0, 0), (1, 0)], 'color': (0, 255, 0)},
    'Z': {'shape': [(-1, 0), (0, 0), (0, 1), (1, 1)], 'color': (255, 0, 0)},
    'J': {'shape': [(-1, -1), (-1, 0), (0, 0), (1, 0)], 'color': (0, 0, 255)},
    'L': {'shape': [(1, -1), (-1, 0), (0, 0), (1, 0)], 'color': (255, 165, 0)}
}

class TetrisGame:
    """
    Represents the state and logic of the Tetris game.
    """
    def __init__(self):
        """
        Initializes the Tetris game state.
        """
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.level = 0
        self.lines_cleared_total = 0
        self.game_over = False
        self.fall_speed_ms = 500  # Initial fall speed in milliseconds.
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()

    def new_piece(self):
        """
        Creates a new random tetromino.

        Returns:
            dict: A dictionary representing the new tetromino.
        """
        piece_type = random.choice(list(TETROMINOES.keys()))
        piece = TETROMINOES[piece_type]
        spawn_y = 1 if piece_type in ['I', 'J', 'L'] else 0
        return {
            'shape': piece['shape'],
            'color': piece['color'],
            'x': COLS // 2,
            'y': spawn_y
        }

    def check_collision(self, shape, pos):
        """
        Checks if a tetromino at a given position collides with the board or its boundaries.

        Args:
            shape (list): The shape of the tetromino.
            pos (tuple): The position of the tetromino (x, y).

        Returns:
            bool: True if there is a collision, False otherwise.
        """
        px, py = pos
        for x, y in shape:
            board_x, board_y = px + x, py + y
            if not (0 <= board_x < COLS and 0 <= board_y < ROWS and self.board[board_y][board_x] is None):
                return True
        return False

    def lock_piece(self):
        """
        Locks the current tetromino in place on the board.
        """
        for x, y in self.current_piece['shape']:
            board_x = self.current_piece['x'] + x
            board_y = self.current_piece['y'] + y
            if 0 <= board_y < ROWS:
                self.board[board_y][board_x] = self.current_piece['color']
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        if self.check_collision(self.current_piece['shape'], (self.current_piece['x'], self.current_piece['y'])):
            self.game_over = True

    def clear_lines(self):
        """
        Finds and clears completed lines, updates the score, and handles leveling.
        """
        full_rows = [i for i, row in enumerate(self.board) if all(row)]

        if not full_rows:
            return

        # Remove full rows from the bottom up.
        for row_index in sorted(full_rows, reverse=True):
            self.board.pop(row_index)

        # Add new empty rows at the top.
        num_cleared = len(full_rows)
        for _ in range(num_cleared):
            self.board.insert(0, [None for _ in range(COLS)])

        # Update score and level.
        self.score += SCORE_MAP.get(num_cleared, 0) * (self.level + 1)
        self.lines_cleared_total += num_cleared
        self.level = self.lines_cleared_total // 10

        # Increase game speed.
        if num_cleared > 0:
            self.fall_speed_ms *= (0.96 ** num_cleared)
            self.fall_speed_ms = max(50, self.fall_speed_ms)

    def move(self, dx, dy):
        """
        Moves the current tetromino.

        Args:
            dx (int): The change in the x-coordinate.
            dy (int): The change in the y-coordinate.

        Returns:
            bool: True if the move was successful, False otherwise.
        """
        if self.game_over: return False
        new_x, new_y = self.current_piece['x'] + dx, self.current_piece['y'] + dy
        if not self.check_collision(self.current_piece['shape'], (new_x, new_y)):
            self.current_piece['x'], self.current_piece['y'] = new_x, new_y
            return True
        return False

    def hard_drop(self):
        """
        Instantly drops the current tetromino to the bottom of the board.
        """
        if self.game_over: return
        while self.move(0, 1):
            pass
        self.lock_piece()

    def drop(self):
        """
        Moves the current tetromino down by one cell, locking it if it collides.
        """
        if not self.move(0, 1):
            self.lock_piece()

    def rotate(self):
        """
        Rotates the current tetromino.
        """
        if self.game_over: return
        if self.current_piece['color'] == TETROMINOES['O']['color']: return
        rotated_shape = [(-y, x) for x, y in self.current_piece['shape']]
        if not self.check_collision(rotated_shape, (self.current_piece['x'], self.current_piece['y'])):
            self.current_piece['shape'] = rotated_shape

def draw_cell(surface, x, y, color, offset_x=0, offset_y=0):
    """
    Draws a single cell on the screen with a 3D effect.

    Args:
        surface (pygame.Surface): The surface to draw on.
        x (int): The x-coordinate of the cell.
        y (int): The y-coordinate of the cell.
        color (tuple): The color of the cell.
        offset_x (int, optional): The x-offset for drawing. Defaults to 0.
        offset_y (int, optional): The y-offset for drawing. Defaults to 0.
    """
    rect = pygame.Rect(offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    
    # Main face of the block
    pygame.draw.rect(surface, color, rect)
    
    # Darker shade for bottom and right edges (shadow)
    shadow_color = (max(0, color[0] - 50), max(0, color[1] - 50), max(0, color[2] - 50))
    pygame.draw.line(surface, shadow_color, rect.bottomleft, rect.bottomright, 3)
    pygame.draw.line(surface, shadow_color, rect.topright, rect.bottomright, 3)

    # Lighter shade for top and left edges (highlight)
    highlight_color = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
    pygame.draw.line(surface, highlight_color, rect.topleft, rect.topright, 3)
    pygame.draw.line(surface, highlight_color, rect.topleft, rect.bottomleft, 3)

    # Inner border for definition
    pygame.draw.rect(surface, GRID_COLOR, rect, 1)

def draw_grid(surface, game_width, game_height):
    """
    Draws the grid lines on the game board.

    Args:
        surface (pygame.Surface): The surface to draw on.
        game_width (int): The width of the game area.
        game_height (int): The height of the game area.
    """
    for x in range(0, GAME_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, game_height))
    for y in range(0, GAME_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (game_width, y))

def draw_board(surface, game):
    """
    Draws the locked pieces on the game board.

    Args:
        surface (pygame.Surface): The surface to draw on.
        game (TetrisGame): The Tetris game object.
    """
    for y, row in enumerate(game.board):
        for x, color in enumerate(row):
            if color:
                draw_cell(surface, x, y, color)

def draw_piece(surface, piece):
    """
    Draws the current tetromino on the screen.

    Args:
        surface (pygame.Surface): The surface to draw on.
        piece (dict): The tetromino to draw.
    """
    for x, y in piece['shape']:
        draw_cell(surface, piece['x'] + x, piece['y'] + y, piece['color'])

def draw_ui(surface, game, font):
    """
    Draws the user interface, including the score, level, and next piece.

    Args:
        surface (pygame.Surface): The surface to draw on.
        game (TetrisGame): The Tetris game object.
        font (pygame.font.Font): The font for the UI text.
    """
    pygame.draw.rect(surface, GRAY, (GAME_WIDTH, 0, SIDE_PANEL_WIDTH, WINDOW_HEIGHT))
    score_text = font.render(f"Score: {game.score}", True, WHITE)
    level_text = font.render(f"Level: {game.level}", True, WHITE)
    next_text = font.render("Next:", True, WHITE)
    surface.blit(score_text, (GAME_WIDTH + 20, 20))
    surface.blit(level_text, (GAME_WIDTH + 20, 60))
    surface.blit(next_text, (GAME_WIDTH + 20, 120))
    for x, y in game.next_piece['shape']:
        draw_cell(surface, x, y, game.next_piece['color'], offset_x=GAME_WIDTH + SIDE_PANEL_WIDTH / 2, offset_y=180)

def draw_game_over(surface, game_over_font):
    """
    Draws the "GAME OVER" message on the screen.

    Args:
        surface (pygame.Surface): The surface to draw on.
        game_over_font (pygame.font.Font): The font for the "GAME OVER" text.
    """
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    text = game_over_font.render("GAME OVER", True, WHITE)
    text_rect = text.get_rect(center=(GAME_WIDTH / 2, GAME_HEIGHT / 2))
    surface.blit(text, text_rect)
    restart_font = pygame.font.Font(None, 30)
    restart_text = restart_font.render("Press R to Restart, Q to Quit", True, WHITE)
    restart_rect = restart_text.get_rect(center=(GAME_WIDTH / 2, GAME_HEIGHT / 2 + 40))
    surface.blit(restart_text, restart_rect)

def main_menu(screen, clock, font, small_font):
    """
    Displays the main menu for Tetris.

    Args:
        screen (pygame.Surface): The screen to draw the menu on.
        clock (pygame.time.Clock): The Pygame clock object.
        font (pygame.font.Font): The font for the title.
        small_font (pygame.font.Font): The font for the buttons.

    Returns:
        str: The action selected by the user ('play', 'settings', or 'quit').
    """
    while True:
        screen.fill(BLACK)
        draw_text("Tetris", font, WHITE, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4)

        settings_button = draw_text("Settings", small_font, WHITE, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 50)
        start_button = draw_text("Start Game", small_font, WHITE, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        quit_button = draw_text("Back to Menu", small_font, WHITE, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return 'play'
                if quit_button.collidepoint(event.pos):
                    return 'quit'
                if settings_button.collidepoint(event.pos):
                    new_volume, status = settings_menu(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, pygame.mixer.music.get_volume())
                    if status == 'quit': return 'quit'
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
    BACKGROUND_COLOR = (0, 0, 0)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (0, 255, 255) # Cyan
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    title_font = pygame.font.Font(None, 70)
    score_font = pygame.font.Font(None, 50)
    button_font = pygame.font.Font(None, 40)

    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("CONGRATULATIONS!", title_font, HIGHLIGHT_COLOR, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3 - 50)
        draw_text(f"You beat Tetris!", score_font, TEXT_COLOR, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3 + 20)
        draw_text(f"Final Score: {final_score}", score_font, TEXT_COLOR, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3 + 80)

        mx, my = pygame.mouse.get_pos()

        # Button dimensions and spacing
        button_width = 250
        button_height = 60
        button_spacing = 20

        back_to_menu_y = WINDOW_HEIGHT / 2 + 100

        back_to_menu_button_rect = pygame.Rect(WINDOW_WIDTH / 2 - button_width / 2, back_to_menu_y, button_width, button_height)

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
    Main function to manage the game states for Tetris.

    Args:
        screen (pygame.Surface): The main screen surface.
        clock (pygame.time.Clock): The Pygame clock object.
    """
    pygame.display.set_caption("Tetris")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)
    game_over_font = pygame.font.Font(None, 50)

    # Game loop for levels
    while True:
        menu_choice = main_menu(screen, clock, font, small_font)
        if menu_choice == 'quit':
            return 0

        current_level = 1
        total_score = 0
        game_outcome = None

        while current_level <= 5:
            game = TetrisGame()
            game.level = current_level - 1 # Set initial level for the game object
            game.score = total_score # Carry over score
            game.fall_speed_ms = 500 - (current_level - 1) * 50 # Increase speed with level
            game.fall_speed_ms = max(50, game.fall_speed_ms) # Minimum fall speed

            FALL_EVENT = pygame.USEREVENT + 1
            pygame.time.set_timer(FALL_EVENT, int(game.fall_speed_ms))
            current_timer_speed = game.fall_speed_ms

            game_running = True
            while game_running:
                screen.fill(BLACK)
                # Event handling.
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        scores.save_score("Tetris", game.score)
                        return game.score
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                        # Pause the game.
                        pause_choice = pause_menu(screen, clock, GAME_WIDTH, GAME_HEIGHT)
                        if pause_choice == 'quit':
                            scores.save_score("Tetris", game.score)
                            return game.score
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                        # Open the settings menu.
                        new_volume, status = settings_menu(screen, clock, GAME_WIDTH, GAME_HEIGHT, pygame.mixer.music.get_volume())
                        if status == 'quit':
                            scores.save_score("Tetris", game.score)
                            return game.score
                    if not game.game_over:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_LEFT: game.move(-1, 0)
                            if event.key == pygame.K_RIGHT: game.move(1, 0)
                            if event.key == pygame.K_DOWN: game.drop()
                            if event.key == pygame.K_UP: game.rotate()
                            if event.key == pygame.K_SPACE: game.hard_drop()
                        if event.type == FALL_EVENT:
                            game.drop()
                    else:  # Game is over.
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r:
                                game_running = False # Exit current game loop to go back to main menu
                            if event.key == pygame.K_q:
                                scores.save_score("Tetris", game.score)
                                return game.score

                # Update fall speed timer if it has changed.
                if game.fall_speed_ms != current_timer_speed:
                    pygame.time.set_timer(FALL_EVENT, int(game.fall_speed_ms))
                    current_timer_speed = game.fall_speed_ms

                # Drawing.
                draw_grid(screen, GAME_WIDTH, GAME_HEIGHT)
                draw_board(screen, game)
                if not game.game_over:
                    draw_piece(screen, game.current_piece)
                draw_ui(screen, game, small_font)
                if game.game_over:
                    draw_game_over(screen, game_over_font)

                pygame.display.flip()
                clock.tick(60)

                # Check for level completion (e.g., clear a certain number of lines)
                # For Tetris, let's say clear 10 lines per level
                if game.lines_cleared_total >= current_level * 10:
                    total_score = game.score
                    current_level += 1
                    if current_level > 5:
                        game_outcome = 'win'
                    else:
                        game_outcome = 'next_level'
                    break # Exit current level loop
                
                if game.game_over:
                    game_outcome = 'game_over'
                    break

            if game_outcome == 'win':
                congratulations_screen(screen, clock, font, total_score)
                break
            elif game_outcome == 'game_over':
                end_choice = end_screen(screen, clock, font, f"Game Over! Score: {total_score}")
                if end_choice == 'quit':
                    return total_score
                break
            elif game_outcome == 'quit':
                return total_score

        scores.save_score("Tetris", total_score)

if __name__ == "__main__":
    # This block runs when the script is executed directly.
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()