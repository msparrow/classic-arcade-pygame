"""
Pygame implementation of the classic game Tic-Tac-Toe.

This script contains the game logic for Tic-Tac-Toe, including the game board,
player turns, and win/tie conditions. It also features a main menu and an end screen.
"""

import pygame
import sys
from config import BLACK, WHITE, GREEN, RED, GRAY
from utils import draw_text, pause_menu, settings_menu

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 600
LINE_WIDTH = 15
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = SCREEN_WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

# Colors
BG_COLOR = BLACK
LINE_COLOR = GRAY
X_COLOR = (255, 165, 0)  # Orange
O_COLOR = WHITE


class TicTacToeGame:
    """
    Manages the Tic-Tac-Toe game states.
    """
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.font = pygame.font.Font(None, 40)
        self.title_font = pygame.font.Font(None, 80)
        self.small_font = pygame.font.Font(None, 36)
        self.board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.player = 'X'
        self.game_over = False
        self.winner = None
        self.state = 'main_menu'

    def run(self):
        """
        Main loop to manage game states.
        """
        while True:
            if self.state == 'main_menu':
                self.main_menu()
            elif self.state == 'game_loop':
                self.game_loop()
            elif self.state == 'quit':
                return

    def main_menu(self):
        """
        Displays the main menu.
        """
        BACKGROUND_COLOR = (30, 10, 30)
        TEXT_COLOR = (255, 255, 255)
        HIGHLIGHT_COLOR = (255, 165, 0)
        BUTTON_COLOR = (50, 50, 50)
        BUTTON_HOVER_COLOR = (80, 80, 80)
        BORDER_COLOR = (150, 150, 150)

        while self.state == 'main_menu':
            self.screen.fill(BACKGROUND_COLOR)
            draw_text("Tic-Tac-Toe", self.title_font, HIGHLIGHT_COLOR, self.screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)

            mx, my = pygame.mouse.get_pos()

            button_width = 250
            button_height = 60
            button_spacing = 20

            start_y = SCREEN_HEIGHT / 2
            quit_y = start_y + button_height + button_spacing

            start_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, start_y, button_width, button_height)
            quit_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, quit_y, button_width, button_height)

            buttons = [
                {"text": "Start Game", "rect": start_button_rect, "action": "play"},
                {"text": "Back to Menu", "rect": quit_button_rect, "action": "quit"}
            ]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = 'quit'
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in buttons:
                        if button["rect"].collidepoint(event.pos):
                            if button["action"] == "play":
                                self.state = 'game_loop'
                                self.restart_game()
                            else:
                                self.state = 'quit'
                                return

            for button in buttons:
                current_button_color = BUTTON_HOVER_COLOR if button["rect"].collidepoint(mx, my) else BUTTON_COLOR
                pygame.draw.rect(self.screen, current_button_color, button["rect"], border_radius=10)
                pygame.draw.rect(self.screen, BORDER_COLOR, button["rect"], 2, border_radius=10)
                draw_text(button["text"], self.small_font, TEXT_COLOR, self.screen, button["rect"].centerx, button["rect"].centery)

            pygame.display.flip()
            self.clock.tick(15)

    def draw_grid(self):
        """
        Draws the game grid.
        """
        self.screen.fill(BG_COLOR)
        # Horizontal lines
        pygame.draw.line(self.screen, LINE_COLOR, (0, SQUARE_SIZE), (SCREEN_WIDTH, SQUARE_SIZE), LINE_WIDTH)
        pygame.draw.line(self.screen, LINE_COLOR, (0, 2 * SQUARE_SIZE), (SCREEN_WIDTH, 2 * SQUARE_SIZE), LINE_WIDTH)
        # Vertical lines
        pygame.draw.line(self.screen, LINE_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, SCREEN_HEIGHT), LINE_WIDTH)
        pygame.draw.line(self.screen, LINE_COLOR, (2 * SQUARE_SIZE, 0), (2 * SQUARE_SIZE, SCREEN_HEIGHT), LINE_WIDTH)

    def draw_figures(self):
        """
        Draws the X's and O's on the board.
        """
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board[row][col] == 'O':
                    pygame.draw.circle(self.screen, O_COLOR, (int(col * SQUARE_SIZE + SQUARE_SIZE // 2), int(row * SQUARE_SIZE + SQUARE_SIZE // 2)), CIRCLE_RADIUS, CIRCLE_WIDTH)
                elif self.board[row][col] == 'X':
                    pygame.draw.line(self.screen, X_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE), CROSS_WIDTH)
                    pygame.draw.line(self.screen, X_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), CROSS_WIDTH)

    def mark_square(self, row, col):
        """
        Marks a square on the board for the current player.
        """
        if self.board[row][col] is None:
            self.board[row][col] = self.player
            return True
        return False

    def check_win(self):
        """
        Checks for a win condition.
        """
        # Vertical win
        for col in range(BOARD_COLS):
            if self.board[0][col] == self.player and self.board[1][col] == self.player and self.board[2][col] == self.player:
                self.draw_win_line((col * SQUARE_SIZE + SQUARE_SIZE // 2, 10), (col * SQUARE_SIZE + SQUARE_SIZE // 2, SCREEN_HEIGHT - 10))
                return True
        # Horizontal win
        for row in range(BOARD_ROWS):
            if self.board[row][0] == self.player and self.board[row][1] == self.player and self.board[row][2] == self.player:
                self.draw_win_line((10, row * SQUARE_SIZE + SQUARE_SIZE // 2), (SCREEN_WIDTH - 10, row * SQUARE_SIZE + SQUARE_SIZE // 2))
                return True
        # Ascending diagonal win
        if self.board[2][0] == self.player and self.board[1][1] == self.player and self.board[0][2] == self.player:
            self.draw_win_line((15, SCREEN_HEIGHT - 15), (SCREEN_WIDTH - 15, 15))
            return True
        # Descending diagonal win
        if self.board[0][0] == self.player and self.board[1][1] == self.player and self.board[2][2] == self.player:
            self.draw_win_line((15, 15), (SCREEN_WIDTH - 15, SCREEN_HEIGHT - 15))
            return True
        return False

    def draw_win_line(self, start, end):
        """
        Draws the line that indicates a win.
        """
        pygame.draw.line(self.screen, RED, start, end, 10)

    def is_board_full(self):
        """
        Checks if the board is full.
        """
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board[row][col] is None:
                    return False
        return True

    def restart_game(self):
        """
        Resets the game to its initial state.
        """
        self.board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.player = 'X'
        self.game_over = False
        self.winner = None
        self.draw_grid()

    def game_loop(self):
        """
        The main game loop.
        """
        while self.state == 'game_loop':
            self.draw_grid()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = 'quit'
                    return

                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    mouseX = event.pos[0]
                    mouseY = event.pos[1]

                    clicked_row = mouseY // SQUARE_SIZE
                    clicked_col = mouseX // SQUARE_SIZE

                    if self.mark_square(clicked_row, clicked_col):
                        if self.check_win():
                            self.winner = self.player
                            self.game_over = True
                        elif self.is_board_full():
                            self.game_over = True
                        else:
                            self.player = 'O' if self.player == 'X' else 'X'

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    if event.key == pygame.K_p:
                        pause_choice = pause_menu(self.screen, self.clock, SCREEN_WIDTH, SCREEN_HEIGHT)
                        if pause_choice == 'quit':
                            self.state = 'main_menu'
                    if event.key == pygame.K_s:
                        settings_menu(self.screen, self.clock, SCREEN_WIDTH, SCREEN_HEIGHT, pygame.mixer.music.get_volume())


            self.draw_figures()

            if self.game_over:
                self.end_screen()

            pygame.display.flip()
            self.clock.tick(60)

    def end_screen(self):
        """
        Displays the end screen.
        """
        BACKGROUND_COLOR = (30, 10, 30)
        TEXT_COLOR = (255, 255, 255)
        HIGHLIGHT_COLOR = (255, 165, 0)
        BUTTON_COLOR = (50, 50, 50)
        BUTTON_HOVER_COLOR = (80, 80, 80)
        BORDER_COLOR = (150, 150, 150)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if self.winner:
            message = f"Player {self.winner} wins!"
        else:
            message = "It's a tie!"
        
        draw_text(message, self.title_font, HIGHLIGHT_COLOR, self.screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)

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

        end_loop = True
        while end_loop:
            mx, my = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = 'quit'
                    end_loop = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in buttons:
                        if button["rect"].collidepoint(event.pos):
                            if button["action"] == "play_again":
                                self.state = 'game_loop'
                                self.restart_game()
                                end_loop = False
                            else:
                                self.state = 'main_menu'
                                end_loop = False

            for button in buttons:
                current_button_color = BUTTON_HOVER_COLOR if button["rect"].collidepoint(mx, my) else BUTTON_COLOR
                pygame.draw.rect(self.screen, current_button_color, button["rect"], border_radius=10)
                pygame.draw.rect(self.screen, BORDER_COLOR, button["rect"], 2, border_radius=10)
                draw_text(button["text"], self.small_font, TEXT_COLOR, self.screen, button["rect"].centerx, button["rect"].centery)

            pygame.display.flip()
            self.clock.tick(15)


def run_game(screen, clock):
    """
    Main function to run the Tic-Tac-Toe game.
    """
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = TicTacToeGame(screen, clock)
    game.run()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tic Tac Toe")
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()
