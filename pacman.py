"""
Pygame implementation of the classic arcade game Pac-Man.

This script contains the game logic for Pac-Man, including player and ghost movement,
- pellet consumption, and collision detection. It also features a main menu and an end screen.
"""

import pygame
import sys
import random
import math
from config import BLACK, WHITE, YELLOW, RED, GREEN, GRAY
from utils import draw_text, pause_menu, settings_menu, Particle, create_explosion
import scores

# --- Constants ---
# Cell size for the grid-based game.
CELL_SIZE = 20
# Maze dimensions.
MAZE_WIDTH, MAZE_HEIGHT = 28, 31
# Screen dimensions derived from maze size and cell size.
SCREEN_WIDTH, SCREEN_HEIGHT = MAZE_WIDTH * CELL_SIZE, MAZE_HEIGHT * CELL_SIZE

# The layout of the maze.
# '#' represents a wall.
# '.' represents a pellet.
# 'o' represents a power pellet.
# 'P' represents the player's starting position.
# 'G' represents a ghost's starting position.
MAZE = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #.##   G  G   ##.#     ",
    "     #.## ######## ##.#     ",
    "######.## #      # ##.######",
    "          #      #          ",
    "######.## #      # ##.######",
    "     #.## ######## ##.#     ",
    "     #.##   G  G   ##.#     ",
    "     #.## ######## ##.#     ",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#o..##.......P .......##..o#",
    "###.##.##.########.##.##.###",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################",
]

class Ghost:
    """
    Represents a ghost in the Pac-Man game.
    """
    def __init__(self, x, y, color):
        """
        Initializes a Ghost object.

        Args:
            x (int): The initial x-coordinate of the ghost.
            y (int): The initial y-coordinate of the ghost.
            color (str): The color of the ghost (used for loading the sprite).
        """
        self.x, self.y = x, y
        self.color = color
        self.direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
        # Load the ghost sprite.
        self.sprite = pygame.image.load(f'assets/sprites/{color}').convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (CELL_SIZE, CELL_SIZE))
        self.animation_timer = 0

    def move(self, maze, player_pos):
        """
        Moves the ghost within the maze.

        Args:
            maze (list): The maze layout.
            player_pos (tuple): The current position of the player.
        """
        # Simple AI: try to move towards the player.
        options = []
        if self.direction == 'UP':
            options = ['UP', 'LEFT', 'RIGHT']
        elif self.direction == 'DOWN':
            options = ['DOWN', 'LEFT', 'RIGHT']
        elif self.direction == 'LEFT':
            options = ['LEFT', 'UP', 'DOWN']
        elif self.direction == 'RIGHT':
            options = ['RIGHT', 'UP', 'DOWN']

        valid_moves = []
        for move in options:
            if move == 'UP' and maze[self.y - 1][self.x] != '#':
                valid_moves.append(move)
            if move == 'DOWN' and maze[self.y + 1][self.x] != '#':
                valid_moves.append(move)
            if move == 'LEFT' and maze[self.y][self.x - 1] != '#':
                valid_moves.append(move)
            if move == 'RIGHT' and maze[self.y][self.x + 1] != '#':
                valid_moves.append(move)

        if valid_moves:
            # Prioritize moves that get closer to the player.
            best_move = self.direction
            min_dist = float('inf')

            for move in valid_moves:
                if move == 'UP':
                    dist = abs(self.x - player_pos[0]) + abs(self.y - 1 - player_pos[1])
                elif move == 'DOWN':
                    dist = abs(self.x - player_pos[0]) + abs(self.y + 1 - player_pos[1])
                elif move == 'LEFT':
                    dist = abs(self.x - 1 - player_pos[0]) + abs(self.y - player_pos[1])
                elif move == 'RIGHT':
                    dist = abs(self.x + 1 - player_pos[0]) + abs(self.y - player_pos[1])
                
                if dist < min_dist:
                    min_dist = dist
                    best_move = move
            
            self.direction = best_move

        # Move the ghost in the chosen direction.
        if self.direction == 'UP':
            self.y -= 1
        elif self.direction == 'DOWN':
            self.y += 1
        elif self.direction == 'LEFT':
            self.x -= 1
        elif self.direction == 'RIGHT':
            self.x += 1
        
        self.animation_timer += 1

    def draw(self, screen):
        """
        Draws the ghost on the screen.

        Args:
            screen (pygame.Surface): The screen to draw on.
        """
        offset_y = math.sin(self.animation_timer * 0.2) * 3
        self.sprite.set_alpha(180)
        screen.blit(self.sprite, (self.x * CELL_SIZE, self.y * CELL_SIZE + offset_y))

class Player:
    """
    Represents the player in the Pac-Man game.
    """
    def __init__(self, x, y):
        """
        Initializes a Player object.

        Args:
            x (int): The initial x-coordinate of the player.
            y (int): The initial y-coordinate of the player.
        """
        self.x, self.y = x, y
        self.dx, self.dy = 0, 0
        # Load the player sprite.
        self.sprite = pygame.image.load('assets/sprites/pacman.png').convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (CELL_SIZE, CELL_SIZE))
        self.animation_timer = 0

    def move(self, dx, dy, maze):
        """
        Moves the player within the maze.

        Args:
            dx (int): The change in the x-coordinate.
            dy (int): The change in the y-coordinate.
            maze (list): The maze layout.
        """
        new_x, new_y = self.x + dx, self.y + dy
        # Check for wall collisions.
        if 0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT and maze[new_y][new_x] != '#':
            self.x, self.y = new_x, new_y
        
        self.animation_timer += 1

    def draw(self, screen):
        """
        Draws the player on the screen.

        Args:
            screen (pygame.Surface): The screen to draw on.
        """
        angle = (self.animation_timer * 10) % 360
        rotated_sprite = pygame.transform.rotate(self.sprite, angle)
        screen.blit(rotated_sprite, (self.x * CELL_SIZE, self.y * CELL_SIZE))

def main_menu(screen, clock, font, small_font):
    """
    Displays the main menu for Pac-Man.

    Args:
        screen (pygame.Surface): The screen to draw the menu on.
        clock (pygame.time.Clock): The Pygame clock object.
        font (pygame.font.Font): The font for the title.
        small_font (pygame.font.Font): The font for the buttons.

    Returns:
        str: The action selected by the user ('play', 'settings', or 'quit').
    """
    # Colors for the main menu UI.
    BACKGROUND_COLOR = (0, 0, 20)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (255, 255, 0)
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    # Main loop for the menu.
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("Pac-Man", font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)

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

def game_loop(screen, clock, font):
    """
    Runs the main game loop for Pac-Man.

    Args:
        screen (pygame.Surface): The main screen surface to draw on.
        clock (pygame.time.Clock): The Pygame clock object for controlling the frame rate.
        font (pygame.font.Font): The font for the UI elements.

    Returns:
        int: The final score of the player.
    """
    pygame.display.set_caption("Pac-Man")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.Font(None, 36)

    # Find the starting position of the player in the maze.
    player_start_pos = next(((x, y) for y, row in enumerate(MAZE) for x, char in enumerate(row) if char == 'P'))
    player = Player(*player_start_pos)

    # Find the starting positions of the ghosts in the maze.
    ghost_start_pos = [(x, y) for y, row in enumerate(MAZE) for x, char in enumerate(row) if char == 'G']
    ghosts = [
        Ghost(ghost_start_pos[0][0], ghost_start_pos[0][1], 'ghost_red.png'),
        Ghost(ghost_start_pos[1][0], ghost_start_pos[1][1], 'ghost_pink.png'),
        Ghost(ghost_start_pos[2][0], ghost_start_pos[2][1], 'ghost_cyan.png'),
        Ghost(ghost_start_pos[3][0], ghost_start_pos[3][1], 'ghost_orange.png')
    ]

    # Create sets of pellets and power pellets from the maze layout.
    pellets = set()
    power_pellets = set()
    for y, row in enumerate(MAZE):
        for x, char in enumerate(row):
            if char == '.':
                pellets.add((x, y))
            elif char == 'o':
                power_pellets.add((x, y))

    # Initialize game state variables.
    score = 0
    lives = 3
    game_over = False
    particles = []

    # Timer for controlling movement speed.
    move_timer = 0
    move_interval = 8  # Lower is faster.

    dx, dy = 0, 0

    # Main game loop.
    running = True
    while running:
        # Event handling.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score
            if event.type == pygame.KEYDOWN:
                # Change player direction based on key presses.
                if event.key == pygame.K_LEFT: dx, dy = -1, 0
                elif event.key == pygame.K_RIGHT: dx, dy = 1, 0
                elif event.key == pygame.K_UP: dx, dy = 0, -1
                elif event.key == pygame.K_DOWN: dx, dy = 0, 1
                elif event.key == pygame.K_p:
                    # Pause the game.
                    pause_choice = pause_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT)
                    if pause_choice == 'quit':
                        return score
                elif event.key == pygame.K_s:
                    # Open the settings menu.
                    new_volume, status = settings_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT, pygame.mixer.music.get_volume())
                    if status == 'quit': return score
                elif event.key == pygame.K_q and game_over:
                    return score

        if not game_over:
            # Move player and ghosts based on the move timer.
            move_timer += 1
            if move_timer >= move_interval:
                player.move(dx, dy, MAZE)
                for ghost in ghosts:
                    ghost.move(MAZE, (player.x, player.y))
                move_timer = 0

            # Check for pellet collision.
            if (player.x, player.y) in pellets:
                pellets.remove((player.x, player.y))
                score += 10
                create_explosion(particles, player.x * CELL_SIZE + CELL_SIZE // 2, player.y * CELL_SIZE + CELL_SIZE // 2, (255, 255, 255), 5)

            # Check for power pellet collision.
            if (player.x, player.y) in power_pellets:
                power_pellets.remove((player.x, player.y))
                score += 50
                create_explosion(particles, player.x * CELL_SIZE + CELL_SIZE // 2, player.y * CELL_SIZE + CELL_SIZE // 2, (0, 255, 0), 20)

            # Check for ghost collision.
            for ghost in ghosts:
                if player.x == ghost.x and player.y == ghost.y:
                    lives -= 1
                    create_explosion(particles, player.x * CELL_SIZE + CELL_SIZE // 2, player.y * CELL_SIZE + CELL_SIZE // 2, (255, 0, 0), 30)
                    if lives <= 0:
                        game_over = True
                    else:
                        # Reset player and ghost positions.
                        player.x, player.y = player_start_pos
                        for i, g in enumerate(ghosts):
                            g.x, g.y = ghost_start_pos[i]

            # Check for win condition.
            if not pellets and not power_pellets:
                game_over = True

        # Update particles
        for p in particles:
            p.update()
        particles = [p for p in particles if p.life > 0]
        particles.append(Particle(player.x * CELL_SIZE + CELL_SIZE // 2, player.y * CELL_SIZE + CELL_SIZE // 2, YELLOW, 3, 10, 0, 0))

        # --- Drawing ---
        screen.fill(BLACK)

        # Draw the maze.
        for y, row in enumerate(MAZE):
            for x, char in enumerate(row):
                if char == '#':
                    pygame.draw.rect(screen, (0, 0, 180), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

        # Draw pellets and power pellets.
        for x, y in pellets:
            pygame.draw.circle(screen, WHITE, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), 2)
        for x, y in power_pellets:
            pygame.draw.circle(screen, GREEN, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), 5)

        # Draw player and ghosts.
        player.draw(screen)
        for ghost in ghosts:
            ghost.draw(screen)
        
        for p in particles:
            p.draw(screen)

        # Draw the UI (score and lives).
        draw_text(f"Score: {score}", font, WHITE, screen, 60, 10)
        draw_text(f"Lives: {lives}", font, WHITE, screen, SCREEN_WIDTH - 60, 10)

        if game_over:
            end_choice = end_screen(screen, clock, font, f"GAME OVER")
            if end_choice == 'quit':
                return score
            # Restart the game.
            player.x, player.y = player_start_pos
            for i, g in enumerate(ghosts):
                g.x, g.y = ghost_start_pos[i]
            pellets = set()
            power_pellets = set()
            for y, row in enumerate(MAZE):
                for x, char in enumerate(row):
                    if char == '.':
                        pellets.add((x, y))
                    elif char == 'o':
                        power_pellets.add((x, y))
            score = 0
            lives = 3
            game_over = False

        pygame.display.flip()
        clock.tick(60)

    return score


def end_screen(screen, clock, font, message):
    """
    Displays the end screen with a message and options to play again or quit.

    Args:
        screen (pygame.Surface): The screen to draw on.
        clock (pygame.time.Clock): The Pygame clock object.
        font (pygame.font.Font): The font for the text.
        message (str): The message to display (e.g., "GAME OVER").

    Returns:
        str: The action selected by the user ('play_again' or 'quit').
    """
    # Colors for the end screen UI.
    BACKGROUND_COLOR = (0, 0, 20)
    TEXT_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (255, 255, 0)
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    title_font = pygame.font.Font(None, 60)
    button_font = pygame.font.Font(None, 40)

    # Main loop for the end screen.
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text(message, title_font, HIGHLIGHT_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)

        mx, my = pygame.mouse.get_pos()

        # Define button properties.
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

        # Event handling for the end screen.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        return button["action"]

        # Draw buttons with hover effects.
        for button in buttons:
            current_button_color = BUTTON_HOVER_COLOR if button["rect"].collidepoint(mx, my) else BUTTON_COLOR
            pygame.draw.rect(screen, current_button_color, button["rect"], border_radius=10)
            pygame.draw.rect(screen, BORDER_COLOR, button["rect"], 2, border_radius=10)
            draw_text(button["text"], button_font, TEXT_COLOR, screen, button["rect"].centerx, button["rect"].centery)

        pygame.display.flip()
        clock.tick(15)

def run_game(screen, clock):
    """
    Main function to manage the game states for Pac-Man.

    Args:
        screen (pygame.Surface): The main screen surface.
        clock (pygame.time.Clock): The Pygame clock object.
    """
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)
    # Main state machine loop.
    while True:
        menu_choice = main_menu(screen, clock, font, small_font)
        if menu_choice == 'quit':
            return 0
        final_score = game_loop(screen, clock, font)
        scores.save_score("Pac-Man", final_score)

if __name__ == "__main__":
    # This block runs when the script is executed directly.
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()

def get_instructions():
    """
    Returns a list of instructions for the Pac-Man game.
    """
    return [
        "Use ARROW keys to move Pac-Man.",
        "Eat all the small white pellets to clear the maze.",
        "Eat the larger green power pellets for bonus points.",
        "Avoid the ghosts!"
    ]
