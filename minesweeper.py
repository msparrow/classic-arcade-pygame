"""
Pygame implementation of the classic game Minesweeper.

This script contains the game logic for Minesweeper, including the grid, cells,
- mine placement, and user interaction for revealing and flagging cells.
"""

import pygame
import sys
import random

# Import shared modules and constants.
from utils import draw_text, pause_menu, settings_menu, Particle, create_explosion

# --- Initialization ---
# Initialize all imported Pygame modules.
pygame.init()

# --- Constants ---
# Grid dimensions and mine count.
# These will be overridden by level settings.
GRID_SIZE, NUM_MINES, CELL_SIZE = 20, 40, 30
# Screen dimensions derived from grid size and cell size.
WIDTH, HEIGHT = GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE

# Colors used in the game.
WHITE, GRAY, DARK_GRAY, BLACK, RED = (255, 255, 255), (192, 192, 192), (128, 128, 128), (0, 0, 0), (255, 0, 0)
# Colors for the numbers indicating adjacent mines.
COLORS = [(0, 0, 255), (0, 128, 0), (255, 0, 0), (0, 0, 128), (128, 0, 0), (0, 128, 128), (0, 0, 0), (128, 128, 128)]

# Level configurations
LEVEL_CONFIGS = {
    1: {'grid_size': 10, 'num_mines': 10},
    2: {'grid_size': 12, 'num_mines': 20},
    3: {'grid_size': 15, 'num_mines': 35},
    4: {'grid_size': 18, 'num_mines': 55},
    5: {'grid_size': 20, 'num_mines': 75},
}

class Cell:
    """
    Represents a single cell in the Minesweeper grid.
    """
    def __init__(self, x, y):
        """
        Initializes a Cell object.

        Args:
            x (int): The x-coordinate of the cell in the grid.
            y (int): The y-coordinate of the cell in the grid.
        """
        self.x, self.y = x, y
        self.is_mine = self.is_revealed = self.is_flagged = False
        self.adjacent_mines = 0
        self.animation_timer = 0

    def draw(self, surface, font):
        """
        Draws the cell on the screen.

        Args:
            surface (pygame.Surface): The surface to draw on.
            font (pygame.font.Font): The font for drawing the number of adjacent mines.
        """
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if self.is_revealed:
            pygame.draw.rect(surface, DARK_GRAY, rect)
            if self.is_mine:
                pygame.draw.circle(surface, RED, rect.center, CELL_SIZE // 3)
            elif self.adjacent_mines > 0:
                text = font.render(str(self.adjacent_mines), True, COLORS[self.adjacent_mines - 1])
                surface.blit(text, text.get_rect(center=rect.center))
        else:
            # 3D effect for unrevealed cells
            pygame.draw.rect(surface, GRAY, rect)
            pygame.draw.line(surface, WHITE, rect.topleft, rect.topright, 2)
            pygame.draw.line(surface, WHITE, rect.topleft, rect.bottomleft, 2)
            pygame.draw.line(surface, DARK_GRAY, rect.bottomleft, rect.bottomright, 2)
            pygame.draw.line(surface, DARK_GRAY, rect.topright, rect.bottomright, 2)

            if self.is_flagged:
                if self.animation_timer < 10:
                    self.animation_timer += 1
                flag_poly = [
                    (rect.centerx, rect.top + 5),
                    (rect.right - 5, rect.centery - 5),
                    (rect.centerx, rect.centery)
                ]
                pygame.draw.polygon(surface, RED, flag_poly)
                pygame.draw.line(surface, BLACK, (rect.centerx, rect.top + 5), (rect.centerx, rect.bottom - 5), 3)
        pygame.draw.rect(surface, BLACK, rect, 1)

def main_menu(screen, clock, font, small_font):
    """
    Displays the main menu for Minesweeper.

    Args:
        screen (pygame.Surface): The screen to draw the menu on.
        clock (pygame.time.Clock): The Pygame clock object.
        font (pygame.font.Font): The font for the title.
        small_font (pygame.font.Font): The font for the buttons.

    Returns:
        str: The action selected by the user ('play', 'settings', or 'quit').
    """
    # Colors for the main menu UI.
    BACKGROUND_COLOR = (10, 30, 10)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (0, 255, 0)
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    # Main loop for the menu.
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("Minesweeper", font, HIGHLIGHT_COLOR, screen, WIDTH / 2, HEIGHT / 4)

        mx, my = pygame.mouse.get_pos()

        # Define button properties.
        button_width = 250
        button_height = 60
        button_spacing = 20

        settings_y = HEIGHT / 2 - 50
        start_y = settings_y + button_height + button_spacing
        quit_y = start_y + button_height + button_spacing

        settings_button_rect = pygame.Rect(WIDTH / 2 - button_width / 2, settings_y, button_width, button_height)
        start_button_rect = pygame.Rect(WIDTH / 2 - button_width / 2, start_y, button_width, button_height)
        quit_button_rect = pygame.Rect(WIDTH / 2 - button_width / 2, quit_y, button_width, button_height)

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
                            new_volume, status = settings_menu(screen, clock, WIDTH, HEIGHT, pygame.mixer.music.get_volume())
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

def create_board(grid_size, num_mines):
    """
    Creates the game board, placing mines and calculating adjacent mine counts.

    Args:
        grid_size (int): The size of the grid (e.g., 10 for a 10x10 board).
        num_mines (int): The number of mines to place on the board.

    Returns:
        list: A 2D list of Cell objects representing the game board.
    """
    board = [[Cell(x, y) for y in range(grid_size)] for x in range(grid_size)]
    # Place mines randomly.
    mines_placed = 0
    while mines_placed < num_mines:
        x, y = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
        if not board[x][y].is_mine:
            board[x][y].is_mine = True
            mines_placed += 1
    # Calculate adjacent mines for each cell.
    for x in range(grid_size):
        for y in range(grid_size):
            if not board[x][y].is_mine:
                count = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < grid_size and 0 <= ny < grid_size and board[nx][ny].is_mine:
                            count += 1
                board[x][y].adjacent_mines = count
    return board

def reveal_cells(board, x, y, grid_size):
    """
    Recursively reveals cells starting from the given coordinates.

    Args:
        board (list): The game board.
        x (int): The x-coordinate of the cell to reveal.
        y (int): The y-coordinate of the cell to reveal.
        grid_size (int): The size of the grid.
    """
    if not (0 <= x < grid_size and 0 <= y < grid_size): return
    cell = board[x][y]
    if cell.is_revealed or cell.is_flagged: return

    cell.is_revealed = True

    # If the cell has no adjacent mines, reveal its neighbors.
    if cell.adjacent_mines == 0 and not cell.is_mine:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    reveal_cells(board, x + dx, y + dy, grid_size)

def draw_end_message(screen, font, message, color, current_level):
    """
    Draws the end game message (win or lose).

    Args:
        screen (pygame.Surface): The screen to draw on.
        font (pygame.font.Font): The font for the message.
        message (str): The message to display.
        color (tuple): The color of the message text.
        current_level (int): The current game level.
    """
    # UI Colors.
    BACKGROUND_COLOR = (10, 30, 10)
    TEXT_COLOR = (255, 255, 255)
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    # Create a semi-transparent overlay.
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # Draw the message.
    title_font = pygame.font.Font(None, 60)
    draw_text(message, title_font, color, screen, WIDTH / 2, HEIGHT / 2 - 50)

    # Draw Restart and Quit buttons.
    button_font = pygame.font.Font(None, 40)
    button_width = 250
    button_height = 60
    button_spacing = 20

    restart_y = HEIGHT / 2 + 20
    quit_y = restart_y + button_height + button_spacing

    restart_button_rect = pygame.Rect(WIDTH / 2 - button_width / 2, restart_y, button_width, button_height)
    quit_button_rect = pygame.Rect(WIDTH / 2 - button_width / 2, quit_y, button_width, button_height)

    mx, my = pygame.mouse.get_pos()

    # Draw Restart button with hover effect.
    current_button_color = BUTTON_HOVER_COLOR if restart_button_rect.collidepoint(mx, my) else BUTTON_COLOR
    pygame.draw.rect(screen, current_button_color, restart_button_rect, border_radius=10)
    pygame.draw.rect(screen, BORDER_COLOR, restart_button_rect, 2, border_radius=10)
    draw_text("Restart (R)", button_font, TEXT_COLOR, screen, restart_button_rect.centerx, restart_button_rect.centery)

    # Draw Quit button with hover effect.
    current_button_color = BUTTON_HOVER_COLOR if quit_button_rect.collidepoint(mx, my) else BUTTON_COLOR
    pygame.draw.rect(screen, current_button_color, quit_button_rect, border_radius=10)
    pygame.draw.rect(screen, BORDER_COLOR, quit_button_rect, 2, border_radius=10)
    draw_text("Quit (Q)", button_font, TEXT_COLOR, screen, quit_button_rect.centerx, quit_button_rect.centery)

def game_loop(screen, clock, font, cell_font, level):
    """
    The main game loop for Minesweeper.

    Args:
        screen (pygame.Surface): The main screen surface to draw on.
        clock (pygame.time.Clock): The Pygame clock object for controlling the frame rate.
        font (pygame.font.Font): The font for UI text.
        cell_font (pygame.font.Font): The font for the numbers in the cells.
        level (int): The current game level.

    Returns:
        str: The outcome of the game ('win', 'game_over', or 'quit').
    """
    pygame.display.set_caption(f"Minesweeper - Level {level}")

    # Get level configurations
    current_grid_size = LEVEL_CONFIGS[level]['grid_size']
    current_num_mines = LEVEL_CONFIGS[level]['num_mines']

    # Adjust screen size based on current_grid_size
    current_width = current_grid_size * CELL_SIZE
    current_height = current_grid_size * CELL_SIZE
    screen = pygame.display.set_mode((current_width, current_height))

    # Initialize game state.
    board = create_board(current_grid_size, current_num_mines)
    game_over = game_won = False
    particles = []

    # Main game loop.
    while True:
        # Event handling.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    # Pause the game.
                    pause_choice = pause_menu(screen, clock, current_width, current_height)
                    if pause_choice == 'quit': return 'quit'
                if event.key == pygame.K_s:
                    # Open the settings menu.
                    new_volume, status = settings_menu(screen, clock, current_width, current_height, pygame.mixer.music.get_volume())
                    if status == 'quit': return 'quit'
                if game_over or game_won:
                    if event.key == pygame.K_r:
                        # Restart the game.
                        return 'restart' # Signal to restart the current level
                    if event.key == pygame.K_q:
                        # Quit to the main menu.
                        return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and not game_won:
                mx, my = event.pos
                grid_x, grid_y = mx // CELL_SIZE, my // CELL_SIZE

                if event.button == 1:  # Left click
                    reveal_cells(board, grid_x, grid_y, current_grid_size)
                    if board[grid_x][grid_y].is_mine:
                        game_over = True
                        # Reveal all mines when the game is over.
                        for row in board:
                            for cell in row:
                                if cell.is_mine:
                                    cell.is_revealed = True
                                    create_explosion(particles, cell.x * CELL_SIZE + CELL_SIZE // 2, cell.y * CELL_SIZE + CELL_SIZE // 2, RED)
                elif event.button == 3:  # Right click
                    if not board[grid_x][grid_y].is_revealed:
                        board[grid_x][grid_y].is_flagged = not board[grid_x][grid_y].is_flagged
                        if board[grid_x][grid_y].is_flagged:
                            board[grid_x][grid_y].animation_timer = 0

        # Check for win condition.
        if not game_over and not game_won:
            revealed_count = sum(c.is_revealed for row in board for c in row)
            if revealed_count == current_grid_size * current_grid_size - current_num_mines:
                game_won = True

        # Drawing.
        screen.fill(DARK_GRAY)
        for x in range(current_grid_size):
            for y in range(current_grid_size):
                board[x][y].draw(screen, cell_font)
        
        # Update and draw particles
        for p in particles:
            p.update()
        particles = [p for p in particles if p.life > 0]
        for p in particles:
            p.draw(screen)

        # Display end game messages.
        if game_over:
            draw_end_message(screen, font, "GAME OVER! R to restart, Q to quit.", RED, level)
        elif game_won:
            draw_end_message(screen, font, "YOU WIN! R to restart, Q to quit.", (0, 255, 0), level)

        pygame.display.flip()
        clock.tick(30)

        if game_over:
            # Wait for user input to restart or quit
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: return 'game_over' # Signal to restart current level
                    if event.key == pygame.K_q: return 'quit'
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    # Check if restart button was clicked
                    restart_button_rect = pygame.Rect(current_width / 2 - 125, current_height / 2 + 20, 250, 60)
                    if restart_button_rect.collidepoint(mx, my): return 'game_over'
                    # Check if quit button was clicked
                    quit_button_rect = pygame.Rect(current_width / 2 - 125, current_height / 2 + 80, 250, 60)
                    if quit_button_rect.collidepoint(mx, my): return 'quit'
        elif game_won:
            # Wait for user input to proceed or quit
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: return 'win' # Signal to proceed to next level
                    if event.key == pygame.K_q: return 'quit'
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    # Check if play again button was clicked
                    play_again_button_rect = pygame.Rect(current_width / 2 - 125, current_height / 2 + 20, 250, 60)
                    if play_again_button_rect.collidepoint(mx, my): return 'win'
                    # Check if quit button was clicked
                    quit_button_rect = pygame.Rect(current_width / 2 - 125, current_height / 2 + 80, 250, 60)
                    if quit_button_rect.collidepoint(mx, my): return 'quit'


def congratulations_screen(screen, clock, font):
    """
    Displays a congratulations screen when the player beats all levels.

    Args:
        screen (pygame.Surface): The screen to draw on.
        clock (pygame.time.Clock): The Pygame clock object.
        font (pygame.font.Font): The font for the text.
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
        draw_text("CONGRATULATIONS!", title_font, HIGHLIGHT_COLOR, screen, WIDTH / 2, HEIGHT / 3 - 50)
        draw_text(f"You beat Minesweeper!", score_font, TEXT_COLOR, screen, WIDTH / 2, HEIGHT / 3 + 20)

        mx, my = pygame.mouse.get_pos()

        # Button dimensions and spacing
        button_width = 250
        button_height = 60
        button_spacing = 20

        back_to_menu_y = HEIGHT / 2 + 100

        back_to_menu_button_rect = pygame.Rect(WIDTH / 2 - button_width / 2, back_to_menu_y, button_width, button_height)

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
    Main function to manage game states for Minesweeper.

    Args:
        screen (pygame.Surface): The main screen surface.
        clock (pygame.time.Clock): The Pygame clock object.
    """
    pygame.display.set_caption("Minesweeper")
    # Fonts for menus and the game.
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)
    cell_font = pygame.font.Font(None, CELL_SIZE)

    # Main state machine loop.
    while True:
        menu_choice = main_menu(screen, clock, font, small_font)
        if menu_choice == 'quit':
            return 0

        current_level = 1
        game_outcome = None

        while current_level <= 5:
            outcome = game_loop(screen, clock, small_font, cell_font, current_level)

            if outcome == 'win':
                current_level += 1
                if current_level > 5:
                    game_outcome = 'win'
                    break
                else:
                    # Display level complete message
                    end_choice = draw_end_message(screen, font, f"Level {current_level - 1} Complete!", (0, 255, 0), current_level)
                    if end_choice == 'quit':
                        game_outcome = 'quit'
                        break
            elif outcome == 'game_over':
                game_outcome = 'game_over'
                break
            elif outcome == 'quit':
                game_outcome = 'quit'
                break

        if game_outcome == 'win':
            congratulations_screen(screen, clock, font)
        elif game_outcome == 'game_over':
            end_choice = draw_end_message(screen, font, "GAME OVER!", RED, current_level)
            if end_choice == 'quit':
                return 0
        elif game_outcome == 'quit':
            return 0

if __name__ == "__main__":
    # This block runs when the script is executed directly.
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()