import pygame
import sys
import random

# --- Initialization ---
pygame.init()

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 15
PADDLE_SPEED = 7
AI_PADDLE_SPEED = 6
WINNING_SCORE = 5

# Colors
BLACK, WHITE = (0, 0, 0), (255, 255, 255)

def draw_text(text, font, color, surface, x, y, center=True):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)
    return textrect

def main_menu(screen, clock, font, small_font):
    while True:
        screen.fill(BLACK)
        draw_text("Pong", font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        start_button = draw_text("Start Game", small_font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        quit_button = draw_text("Back to Menu", small_font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return 'play'
                if quit_button.collidepoint(event.pos):
                    return 'quit'

        pygame.display.flip()
        clock.tick(15)

def game_loop(screen, clock, font):
    player_paddle = pygame.Rect(50, SCREEN_HEIGHT / 2 - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ai_paddle = pygame.Rect(SCREEN_WIDTH - 50 - PADDLE_WIDTH, SCREEN_HEIGHT / 2 - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(SCREEN_WIDTH / 2 - BALL_SIZE / 2, SCREEN_HEIGHT / 2 - BALL_SIZE / 2, BALL_SIZE, BALL_SIZE)

    ball_speed_x = 7 * random.choice((1, -1))
    ball_speed_y = 7 * random.choice((1, -1))

    player_score, ai_score = 0, 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Allows quitting from the game window
                return 'quit'

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN]:
            player_paddle.y += PADDLE_SPEED

        # Keep player paddle on screen
        player_paddle.y = max(0, min(player_paddle.y, SCREEN_HEIGHT - PADDLE_HEIGHT))

        # Ball movement
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Ball collision with top/bottom walls
        if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
            ball_speed_y *= -1

        # Ball collision with paddles
        if ball.colliderect(player_paddle) or ball.colliderect(ai_paddle):
            ball_speed_x *= -1.1 # Increase speed on hit
            ball_speed_y *= 1.1

        # Scoring
        if ball.left <= 0:
            ai_score += 1
            ball.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            ball_speed_x = 7 * random.choice((1, -1))
            ball_speed_y = 7 * random.choice((1, -1))
        if ball.right >= SCREEN_WIDTH:
            player_score += 1
            ball.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            ball_speed_x = 7 * random.choice((1, -1))
            ball_speed_y = 7 * random.choice((1, -1))

        # AI movement
        if ai_paddle.centery < ball.centery:
            ai_paddle.y += AI_PADDLE_SPEED
        if ai_paddle.centery > ball.centery:
            ai_paddle.y -= AI_PADDLE_SPEED
        ai_paddle.y = max(0, min(ai_paddle.y, SCREEN_HEIGHT - PADDLE_HEIGHT))

        # --- Drawing ---
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, player_paddle)
        pygame.draw.rect(screen, WHITE, ai_paddle)
        pygame.draw.ellipse(screen, WHITE, ball)
        pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH / 2, 0), (SCREEN_WIDTH / 2, SCREEN_HEIGHT))

        # Draw scores
        draw_text(str(player_score), font, WHITE, screen, SCREEN_WIDTH / 4, 50)
        draw_text(str(ai_score), font, WHITE, screen, SCREEN_WIDTH * 3 / 4, 50)

        # Check for winner
        if player_score >= WINNING_SCORE:
            return "Player Wins!"
        if ai_score >= WINNING_SCORE:
            return "AI Wins!"

        pygame.display.flip()
        clock.tick(60)

def end_screen(screen, clock, font, small_font, message):
    while True:
        screen.fill(BLACK)
        draw_text(message, font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        play_again_button = draw_text("Play Again", small_font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        quit_button = draw_text("Back to Menu", small_font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_button.collidepoint(event.pos):
                    return 'play_again'
                if quit_button.collidepoint(event.pos):
                    return 'quit'

        pygame.display.flip()
        clock.tick(15)

def run_game(screen, clock):
    pygame.display.set_caption("Pong")
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)

    while True:
        menu_choice = main_menu(screen, clock, font, small_font)
        if menu_choice == 'quit':
            return

        winner_message = game_loop(screen, clock, font)
        if winner_message == 'quit':
            return
        
        end_choice = end_screen(screen, clock, font, small_font, winner_message)
        if end_choice == 'quit':
            return

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()