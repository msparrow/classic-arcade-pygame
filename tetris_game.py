import pygame
import sys
import random

# Import shared modules and constants.
from config import BLACK, WHITE, GRAY, DEFAULT_MUSIC_VOLUME, GREEN, RED, YELLOW
from utils import draw_text, pause_menu, settings_menu, create_explosion
import scores


# Game constants
CELL_SIZE = 30
COLS = 10
ROWS = 20
GAME_WIDTH, GAME_HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE
WINDOW_WIDTH, WINDOW_HEIGHT = GAME_WIDTH + 200, GAME_HEIGHT

# Tetromino shapes and colors
SHAPES = [
    {'shape': [[1, 1, 1, 1]], 'color': (0, 255, 255)},  # I
    {'shape': [[1, 1, 0], [0, 1, 1]], 'color': (255, 0, 0)},  # Z
    {'shape': [[0, 1, 1], [1, 1, 0]], 'color': (0, 255, 0)},  # S
    {'shape': [[1, 1, 1], [0, 1, 0]], 'color': (160, 32, 240)},  # T
    {'shape': [[1, 1], [1, 1]], 'color': (255, 255, 0)},  # O
    {'shape': [[1, 0, 0], [1, 1, 1]], 'color': (0, 0, 255)},  # L
    {'shape': [[0, 0, 1], [1, 1, 1]], 'color': (255, 165, 0)}   # J
]

def main_menu(screen, clock, font, small_font):
    """
    Displays the main menu for Tetris.
    """
    while True:
        screen.fill(BLACK)
        draw_text("Tetris", font, WHITE, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4)

        mx, my = pygame.mouse.get_pos()

        play_button = pygame.Rect(WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2 - 25, 200, 50)
        quit_button = pygame.Rect(WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2 + 50, 200, 50)

        if play_button.collidepoint((mx, my)):
            pygame.draw.rect(screen, (0, 200, 0), play_button)
        else:
            pygame.draw.rect(screen, GREEN, play_button)
        if quit_button.collidepoint((mx, my)):
            pygame.draw.rect(screen, (200, 0, 0), quit_button)
        else:
            pygame.draw.rect(screen, RED, quit_button)

        draw_text("Play", small_font, BLACK, screen, play_button.centerx, play_button.centery)
        draw_text("Quit", small_font, BLACK, screen, quit_button.centerx, quit_button.centery)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    return 'play'
                if quit_button.collidepoint(event.pos):
                    return 'quit'

        pygame.display.flip()
        clock.tick(15)

def congratulations_screen(screen, clock, font, score):
    """
    Displays a congratulations message when the player completes all levels.
    """
    while True:
        screen.fill(BLACK)
        draw_text("Congratulations!", font, YELLOW, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3)
        draw_text(f"Final Score: {score}", font, WHITE, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        draw_text("Press any key to return to menu.", font, GRAY, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT * 2 / 3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                return

        pygame.display.flip()
        clock.tick(15)

def end_screen(screen, clock, font, message):
    """
    Displays the end screen with a message and options to play again or quit.
    """
    BACKGROUND_COLOR = (0, 0, 0)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (255, 0, 0)
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    title_font = pygame.font.Font(None, 60)
    button_font = pygame.font.Font(None, 40)

    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text(message, title_font, HIGHLIGHT_COLOR, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3)

        mx, my = pygame.mouse.get_pos()

        button_width = 250
        button_height = 60
        button_spacing = 20

        play_again_y = WINDOW_HEIGHT / 2 + 20
        quit_y = play_again_y + button_height + button_spacing

        play_again_button_rect = pygame.Rect(WINDOW_WIDTH / 2 - button_width / 2, play_again_y, button_width, button_height)
        quit_button_rect = pygame.Rect(WINDOW_WIDTH / 2 - button_width / 2, quit_y, button_width, button_height)

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
    """
    pygame.display.set_caption("Tetris")
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)
    game_over_font = pygame.font.Font(None, 50)
    particles = []

    while True:
        menu_choice = main_menu(screen, clock, font, small_font)
        if menu_choice == 'quit':
            return 0

        current_level = 1
        total_score = 0
        game_outcome = None

        while current_level <= 5:
            game = TetrisGame()
            game.level = current_level - 1
            game.score = total_score
            game.fall_speed_ms = 500 - (current_level - 1) * 50
            game.fall_speed_ms = max(50, game.fall_speed_ms)

            FALL_EVENT = pygame.USEREVENT + 1
            pygame.time.set_timer(FALL_EVENT, int(game.fall_speed_ms))
            current_timer_speed = game.fall_speed_ms

            game_running = True
            while game_running:
                screen.fill(BLACK)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        scores.save_score("Tetris", game.score)
                        return game.score
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                        pause_choice = pause_menu(screen, clock, GAME_WIDTH, GAME_HEIGHT)
                        if pause_choice == 'quit':
                            scores.save_score("Tetris", game.score)
                            return game.score
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
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
                    else:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r:
                                game_running = False
                            if event.key == pygame.K_q:
                                scores.save_score("Tetris", game.score)
                                return game.score

                if game.fall_speed_ms != current_timer_speed:
                    pygame.time.set_timer(FALL_EVENT, int(game.fall_speed_ms))
                    current_timer_speed = game.fall_speed_ms

                ghost_piece = game.current_piece.copy()
                ghost_piece['shape'] = list(game.current_piece['shape'])
                while not game.check_collision(ghost_piece['shape'], (ghost_piece['x'], ghost_piece['y'] + 1)):
                    ghost_piece['y'] += 1

                if game.lines_cleared_total > 0 and len(particles) == 0:
                    for y in range(ROWS):
                        if all(game.board[y]):
                            for x in range(COLS):
                                create_explosion(particles, x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2, (255, 255, 255))

                screen.fill((20, 20, 40))
                draw_grid(screen, GAME_WIDTH, GAME_HEIGHT)
                draw_board(screen, game)
                if not game.game_over:
                    # Draw ghost piece
                    for y, row in enumerate(ghost_piece['shape']):
                        for x, cell in enumerate(row):
                            if cell:
                                draw_cell(screen, ghost_piece['x'] + x, ghost_piece['y'] + y, (80, 80, 80))
                    draw_piece(screen, game.current_piece)
                draw_ui(screen, game, small_font)
                
                for p in particles:
                    p.update()
                particles = [p for p in particles if p.life > 0]
                for p in particles:
                    p.draw(screen)

                if game.game_over:
                    draw_game_over(screen, game_over_font)

                pygame.display.flip()
                clock.tick(60)

                if game.lines_cleared_total >= current_level * 10:
                    total_score = game.score
                    current_level += 1
                    if current_level > 5:
                        game_outcome = 'win'
                    else:
                        game_outcome = 'next_level'
                    break
                
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

class TetrisGame:
    def __init__(self):
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.level = 0
        self.lines_cleared_total = 0
        self.game_over = False
        self.fall_speed_ms = 500
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()

    def new_piece(self):
        shape = random.choice(SHAPES)
        return {
            'shape': shape['shape'],
            'color': shape['color'],
            'x': COLS // 2 - len(shape['shape'][0]) // 2,
            'y': 0
        }

    def check_collision(self, shape, pos):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    board_x, board_y = pos[0] + x, pos[1] + y
                    if not (0 <= board_x < COLS and 0 <= board_y < ROWS and not self.board[board_y][board_x]):
                        return True
        return False

    def move(self, dx, dy):
        if not self.check_collision(self.current_piece['shape'], (self.current_piece['x'] + dx, self.current_piece['y'] + dy)):
            self.current_piece['x'] += dx
            self.current_piece['y'] += dy

    def drop(self):
        if not self.check_collision(self.current_piece['shape'], (self.current_piece['x'], self.current_piece['y'] + 1)):
            self.current_piece['y'] += 1
        else:
            self.lock_piece()

    def hard_drop(self):
        while not self.check_collision(self.current_piece['shape'], (self.current_piece['x'], self.current_piece['y'] + 1)):
            self.current_piece['y'] += 1
        self.lock_piece()

    def rotate(self):
        shape = self.current_piece['shape']
        rotated_shape = [list(row) for row in zip(*shape[::-1])]
        if not self.check_collision(rotated_shape, (self.current_piece['x'], self.current_piece['y'])):
            self.current_piece['shape'] = rotated_shape

    def lock_piece(self):
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.board[self.current_piece['y'] + y][self.current_piece['x'] + x] = self.current_piece['color']
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        if self.check_collision(self.current_piece['shape'], (self.current_piece['x'], self.current_piece['y'])):
            self.game_over = True

    def clear_lines(self):
        lines_cleared = 0
        new_board = [row for row in self.board if not all(row)]
        lines_cleared = ROWS - len(new_board)
        for _ in range(lines_cleared):
            new_board.insert(0, [0 for _ in range(COLS)])
        self.board = new_board
        self.score += lines_cleared * 100 * (self.level + 1)
        self.lines_cleared_total += lines_cleared
        if self.lines_cleared_total > 0 and self.lines_cleared_total % 10 == 0:
            self.level += 1
            self.fall_speed_ms = max(100, 500 - self.level * 50)

def draw_grid(screen, width, height):
    for x in range(0, width, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, height))
    for y in range(0, height, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (width, y))

def draw_board(screen, game):
    for y, row in enumerate(game.board):
        for x, cell in enumerate(row):
            if cell:
                draw_cell(screen, x, y, cell)

def draw_cell(screen, x, y, color):
    pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, (255, 255, 255), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

def draw_piece(screen, piece):
    for y, row in enumerate(piece['shape']):
        for x, cell in enumerate(row):
            if cell:
                draw_cell(screen, piece['x'] + x, piece['y'] + y, piece['color'])

def draw_ui(screen, game, font):
    draw_text(f"Score: {game.score}", font, WHITE, screen, WINDOW_WIDTH - 150, 50)
    draw_text(f"Level: {game.level + 1}", font, WHITE, screen, WINDOW_WIDTH - 150, 100)
    draw_text(f"Lines: {game.lines_cleared_total}", font, WHITE, screen, WINDOW_WIDTH - 150, 150)
    draw_text("Next:", font, WHITE, screen, WINDOW_WIDTH - 150, 250)
    for y, row in enumerate(game.next_piece['shape']):
        for x, cell in enumerate(row):
            if cell:
                draw_cell(screen, (WINDOW_WIDTH - 180) // CELL_SIZE + x, 300 // CELL_SIZE + y, game.next_piece['color'])

def draw_game_over(screen, font):
    draw_text("Game Over", font, (255, 0, 0), screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 50)
    draw_text("Press 'R' to Restart", font, WHITE, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 20)

if __name__ == '__main__':
    pygame.init()
    pygame.mixer.init()
    try:
        pygame.mixer.music.load('assets/music/menu_theme.wav')
        pygame.mixer.music.set_volume(DEFAULT_MUSIC_VOLUME)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        print(f"Warning: Music file not found or couldn't be played. {e}")

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()