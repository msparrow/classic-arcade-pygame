import pygame
import sys
import random

# --- Initialization ---
pygame.init()

# --- Constants ---
GRID_SIZE, NUM_MINES, CELL_SIZE = 20, 40, 30
WIDTH, HEIGHT = GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE

WHITE, GRAY, DARK_GRAY, BLACK, RED = (255, 255, 255), (192, 192, 192), (128, 128, 128), (0, 0, 0), (255, 0, 0)
COLORS = [(0, 0, 255), (0, 128, 0), (255, 0, 0), (0, 0, 128), (128, 0, 0), (0, 128, 128), (0, 0, 0), (128, 128, 128)]

class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.is_mine = self.is_revealed = self.is_flagged = False
        self.adjacent_mines = 0

    def draw(self, surface, font):
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if self.is_revealed:
            pygame.draw.rect(surface, DARK_GRAY, rect)
            if self.is_mine:
                pygame.draw.circle(surface, RED, rect.center, CELL_SIZE // 3)
            elif self.adjacent_mines > 0:
                text = font.render(str(self.adjacent_mines), True, COLORS[self.adjacent_mines - 1])
                surface.blit(text, text.get_rect(center=rect.center))
        else:
            pygame.draw.rect(surface, GRAY, rect)
            if self.is_flagged:
                pygame.draw.line(surface, RED, rect.topleft, rect.bottomright, 2)
                pygame.draw.line(surface, RED, rect.topright, rect.bottomleft, 2)
        pygame.draw.rect(surface, BLACK, rect, 1)

def create_board():
    board = [[Cell(x, y) for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
    mines_placed = 0
    while mines_placed < NUM_MINES:
        x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        if not board[x][y].is_mine:
            board[x][y].is_mine = True
            mines_placed += 1
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if not board[x][y].is_mine:
                count = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and board[nx][ny].is_mine:
                            count += 1
                board[x][y].adjacent_mines = count
    return board

def reveal_cells(board, x, y):
    if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE): return
    cell = board[x][y]
    if cell.is_revealed or cell.is_flagged: return

    cell.is_revealed = True

    if cell.adjacent_mines == 0 and not cell.is_mine:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    reveal_cells(board, x + dx, y + dy)

def draw_end_message(screen, font, message, color):
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    pygame.draw.rect(screen, BLACK, text_rect.inflate(20, 20))
    screen.blit(text, text_rect)

def run_game(screen, clock):
    pygame.display.set_caption("Minesweeper")
    # Resize screen for this game
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.Font(None, 28) # Adjusted font size for end-game messages
    cell_font = pygame.font.Font(None, CELL_SIZE)
    board = create_board()
    game_over = game_won = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Allows quitting from the game window
                return
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and not game_won:
                mx, my = event.pos
                grid_x, grid_y = mx // CELL_SIZE, my // CELL_SIZE

                if event.button == 1:
                    reveal_cells(board, grid_x, grid_y)
                    if board[grid_x][grid_y].is_mine:
                        game_over = True
                        for row in board:
                            for cell in row:
                                if cell.is_mine: cell.is_revealed = True
                elif event.button == 3:
                    if not board[grid_x][grid_y].is_revealed:
                        board[grid_x][grid_y].is_flagged = not board[grid_x][grid_y].is_flagged

            if event.type == pygame.KEYDOWN and (game_over or game_won):
                if event.key == pygame.K_r:
                    board = create_board()
                    game_over = game_won = False
                if event.key == pygame.K_q:
                    return # Quit to menu

        if not game_over and not game_won:
            revealed_count = sum(c.is_revealed for row in board for c in row)
            if revealed_count == GRID_SIZE * GRID_SIZE - NUM_MINES:
                game_won = True

        screen.fill(DARK_GRAY)
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                board[x][y].draw(screen, cell_font)

        if game_over:
            draw_end_message(screen, font, "GAME OVER! R to restart, Q to quit.", RED)
        elif game_won:
            draw_end_message(screen, font, "YOU WIN! R to restart, Q to quit.", (0, 255, 0))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    pygame.init()
    # The screen is created here for standalone running
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()