import pygame
import sys
import random

# --- Initialization ---
pygame.init()

# --- Game Constants ---
COLS, ROWS = 10, 20
CELL_SIZE = 30
GAME_WIDTH, GAME_HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE
SIDE_PANEL_WIDTH = 150
WINDOW_WIDTH, WINDOW_HEIGHT = GAME_WIDTH + SIDE_PANEL_WIDTH, GAME_HEIGHT

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
GRID_COLOR = (80, 80, 80)

# Scoring based on number of lines cleared at once
SCORE_MAP = {1: 40, 2: 100, 3: 300, 4: 1200}

# --- Tetromino Shapes and Colors ---
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
    def __init__(self):
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.level = 0
        self.lines_cleared_total = 0
        self.game_over = False
        self.fall_speed_ms = 500  # Initial fall speed in milliseconds
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()

    def new_piece(self):
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
        px, py = pos
        for x, y in shape:
            board_x, board_y = px + x, py + y
            if not (0 <= board_x < COLS and 0 <= board_y < ROWS and self.board[board_y][board_x] is None):
                return True
        return False

    def lock_piece(self):
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
        """Finds and clears completed lines, updates score, and handles leveling."""
        # Identify full rows
        full_rows = [i for i, row in enumerate(self.board) if all(row)]

        if not full_rows:
            return

        # Remove full rows from bottom to top
        for row_index in sorted(full_rows, reverse=True):
            self.board.pop(row_index)

        # Add new empty rows at the top
        num_cleared = len(full_rows)
        for _ in range(num_cleared):
            self.board.insert(0, [None for _ in range(COLS)])

        self.score += SCORE_MAP.get(num_cleared, 0) * (self.level + 1)
        self.lines_cleared_total += num_cleared
        self.level = self.lines_cleared_total // 10

        # Increase speed for each line cleared
        if num_cleared > 0:
            self.fall_speed_ms *= (0.96 ** num_cleared)
            self.fall_speed_ms = max(50, self.fall_speed_ms) # Enforce a speed limit

    def move(self, dx, dy):
        if self.game_over: return False
        new_x, new_y = self.current_piece['x'] + dx, self.current_piece['y'] + dy
        if not self.check_collision(self.current_piece['shape'], (new_x, new_y)):
            self.current_piece['x'], self.current_piece['y'] = new_x, new_y
            return True
        return False

    def hard_drop(self):
        if self.game_over: return
        while self.move(0, 1):
            pass  # Keep moving down until it can't anymore
        self.lock_piece()

    def drop(self):
        if not self.move(0, 1):
            self.lock_piece()

    def rotate(self):
        if self.game_over: return
        if self.current_piece['color'] == TETROMINOES['O']['color']: return # 'O' doesn't rotate
        rotated_shape = [(-y, x) for x, y in self.current_piece['shape']]
        if not self.check_collision(rotated_shape, (self.current_piece['x'], self.current_piece['y'])):
            self.current_piece['shape'] = rotated_shape

def draw_cell(surface, x, y, color, offset_x=0, offset_y=0):
    rect = pygame.Rect(offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, GRID_COLOR, rect, 1)

def draw_grid(surface, game_width, game_height):
    for x in range(0, GAME_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, game_height))
    for y in range(0, GAME_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (game_width, y))

def draw_board(surface, game):
    for y, row in enumerate(game.board):
        for x, color in enumerate(row):
            if color:
                draw_cell(surface, x, y, color)

def draw_piece(surface, piece):
    for x, y in piece['shape']:
        draw_cell(surface, piece['x'] + x, piece['y'] + y, piece['color'])

def draw_ui(surface, game, font):
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

def run_game(screen, clock):
    pygame.display.set_caption("Tetris")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) # Resize for this game
    font = pygame.font.Font(None, 36)
    game_over_font = pygame.font.Font(None, 50)

    game = TetrisGame()
    FALL_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(FALL_EVENT, int(game.fall_speed_ms))
    current_timer_speed = game.fall_speed_ms

    while True:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Allows quitting from the game window
                return
            if not game.game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT: game.move(-1, 0)
                    if event.key == pygame.K_RIGHT: game.move(1, 0)
                    if event.key == pygame.K_DOWN: game.drop()
                    if event.key == pygame.K_UP: game.rotate()
                    if event.key == pygame.K_SPACE: game.hard_drop()
                if event.type == FALL_EVENT:
                    game.drop()
            else: # Game is over
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        run_game(screen, clock) # Recurse to restart
                        return
                    if event.key == pygame.K_q:
                        return

        # --- Speed Update Logic ---
        # If the game's internal speed has changed, update the timer
        if game.fall_speed_ms != current_timer_speed:
            pygame.time.set_timer(FALL_EVENT, int(game.fall_speed_ms))
            current_timer_speed = game.fall_speed_ms

        # --- Drawing ---
        draw_grid(screen, GAME_WIDTH, GAME_HEIGHT)
        draw_board(screen, game)
        if not game.game_over:
            draw_piece(screen, game.current_piece)
        draw_ui(screen, game, font)
        if game.game_over:
            draw_game_over(screen, game_over_font)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()