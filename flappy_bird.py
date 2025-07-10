import pygame
import random
import sys
import scores

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 235)  # A nice light blue for the sky
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)

# Game variables
GRAVITY = 0.25

# Font
GAME_FONT = pygame.font.Font(None, 40)

# Pipes
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1500)
pipe_height = [200, 300, 400]

def draw_floor(screen):
    """Draws a simple floor."""
    pygame.draw.rect(screen, (222, 216, 149), (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
    pygame.draw.rect(screen, (140, 129, 86), (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100), 5)


def create_pipe():
    """Creates a new pipe."""
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pygame.Rect(SCREEN_WIDTH, random_pipe_pos, 52, 320)
    top_pipe = pygame.Rect(SCREEN_WIDTH, random_pipe_pos - 450, 52, 320)
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    """Moves the pipes to the left."""
    for pipe in pipes:
        pipe.centerx -= 2
    return [pipe for pipe in pipes if pipe.right > -10]


def draw_pipes(screen, pipes):
    """Draws the pipes on the screen."""
    for pipe in pipes:
        if pipe.bottom >= SCREEN_HEIGHT:
            pygame.draw.rect(screen, GREEN, pipe)
            # Pipe head
            pygame.draw.rect(screen, GREEN, (pipe.x - 2, pipe.y, 56, 20))
        else:
            pygame.draw.rect(screen, GREEN, pipe)
            # Pipe head
            pygame.draw.rect(screen, GREEN, (pipe.x - 2, pipe.bottom - 20, 56, 20))


def check_collision(pipes, bird_rect):
    """Checks for collisions with pipes or screen boundaries."""
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False

    if bird_rect.top <= -10 or bird_rect.bottom >= SCREEN_HEIGHT - 100:
        return False

    return True

def score_display(screen, game_state, score, high_score):
    """Displays the score."""
    if game_state == 'main_game':
        score_surface = GAME_FONT.render(str(int(score)), True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(score_surface, score_rect)
    if game_state == 'game_over':
        score_surface = GAME_FONT.render(f'Score: {int(score)}', True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(score_surface, score_rect)

        high_score_surface = GAME_FONT.render(f'High score: {int(high_score)}', True, WHITE)
        high_score_rect = high_score_surface.get_rect(center=(SCREEN_WIDTH // 2, 425))
        screen.blit(high_score_surface, high_score_rect)

        # Game over message
        game_over_surface = GAME_FONT.render("Game Over", True, WHITE)
        game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_surface, game_over_rect)

        restart_surface = GAME_FONT.render("Press Space to Restart", True, WHITE)
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(restart_surface, restart_rect)


def update_score(score, high_score):
    """Updates the high score."""
    if score > high_score:
        high_score = score
    return high_score

def run_game(screen, clock):
    """Main game loop."""
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird")
    
    bird_movement = 0
    game_active = True
    score = 0
    high_score = scores.load_scores().get("Flappy Bird", 0)
    pipe_list = []
    bird_rect = pygame.Rect(65, SCREEN_HEIGHT // 2 - 50, 34, 24)


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active:
                    bird_movement = 0
                    bird_movement -= 6
                if event.key == pygame.K_SPACE and not game_active:
                    game_active = True
                    pipe_list.clear()
                    bird_rect.center = (65, SCREEN_HEIGHT // 2 - 50)
                    bird_movement = 0
                    score = 0
                if event.key == pygame.K_ESCAPE:
                    return

            if event.type == SPAWNPIPE:
                pipe_list.extend(create_pipe())


        screen.fill(BLUE) # Sky blue background

        if game_active:
            # Bird
            bird_movement += GRAVITY
            bird_rect.centery += int(bird_movement)
            pygame.draw.ellipse(screen, YELLOW, bird_rect) # Simple bird

            # Pipes
            pipe_list = move_pipes(pipe_list)
            draw_pipes(screen, pipe_list)

            # Collision
            game_active = check_collision(pipe_list, bird_rect)

            # Score
            # A simple way to score: check if a pipe has passed the bird
            for pipe in pipe_list:
                if pipe.centerx == bird_rect.centerx:
                    score += 0.5 # Increment by 0.5 because we have top and bottom pipes

            score_display(screen, 'main_game', score, high_score)
        else:
            high_score = update_score(score, high_score)
            scores.save_score("Flappy Bird", high_score)
            score_display(screen, 'game_over', score, high_score)


        # Floor
        draw_floor(screen)

        pygame.display.update()
        clock.tick(60)
