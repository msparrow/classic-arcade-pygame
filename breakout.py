import pygame
import sys

# --- Initialization ---
pygame.init()

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 20
BALL_RADIUS = 10
PADDLE_SPEED = 10
BALL_SPEED_INITIAL = 6

BRICK_WIDTH, BRICK_HEIGHT = 75, 30
BRICK_ROWS, BRICK_COLS = 5, 10
BRICK_GAP = 5

BLACK, WHITE = (0, 0, 0), (255, 255, 255)
PADDLE_COLOR = (0, 150, 255)
BALL_COLOR = (255, 255, 0)
BRICK_COLORS = [(255, 0, 0), (255, 165, 0), (0, 255, 0), (0, 0, 255), (128, 0, 128)]

def create_bricks():
    bricks = []
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            x = col * (BRICK_WIDTH + BRICK_GAP) + (SCREEN_WIDTH - (BRICK_COLS * (BRICK_WIDTH + BRICK_GAP))) / 2
            y = row * (BRICK_HEIGHT + BRICK_GAP) + 50
            brick = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
            bricks.append({'rect': brick, 'color': BRICK_COLORS[row % len(BRICK_COLORS)]})
    return bricks

def draw_text(text, font, color, surface, x, y, center=True):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y)) if center else textobj.get_rect(topleft=(x, y))
    surface.blit(textobj, textrect)
    return textrect

def run_game(screen, clock):
    pygame.display.set_caption("Breakout")
    font = pygame.font.Font(None, 36)
    paddle = pygame.Rect(SCREEN_WIDTH / 2 - PADDLE_WIDTH / 2, SCREEN_HEIGHT - 40, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(SCREEN_WIDTH / 2 - BALL_RADIUS, paddle.y - BALL_RADIUS * 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
    ball_speed_x, ball_speed_y = BALL_SPEED_INITIAL, -BALL_SPEED_INITIAL
    bricks = create_bricks()
    score, lives = 0, 3

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Allows quitting from the game window
                return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: paddle.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT]: paddle.x += PADDLE_SPEED
        paddle.x = max(0, min(paddle.x, SCREEN_WIDTH - PADDLE_WIDTH))

        ball.x += ball_speed_x
        ball.y += ball_speed_y

        if ball.left <= 0 or ball.right >= SCREEN_WIDTH: ball_speed_x *= -1
        if ball.top <= 0: ball_speed_y *= -1

        if ball.colliderect(paddle):
            ball_speed_y *= -1
            offset = (ball.centerx - paddle.centerx) / (PADDLE_WIDTH / 2)
            ball_speed_x = offset * BALL_SPEED_INITIAL

        for brick_info in bricks[:]:
            if ball.colliderect(brick_info['rect']):
                bricks.remove(brick_info)
                ball_speed_y *= -1
                score += 10
                break

        if ball.top >= SCREEN_HEIGHT:
            lives -= 1
            if lives <= 0:
                if end_screen(screen, clock, font, f"Game Over! Score: {score}") == 'quit':
                    return
                # Restart
                paddle = pygame.Rect(SCREEN_WIDTH / 2 - PADDLE_WIDTH / 2, SCREEN_HEIGHT - 40, PADDLE_WIDTH, PADDLE_HEIGHT)
                ball = pygame.Rect(SCREEN_WIDTH / 2 - BALL_RADIUS, paddle.y - BALL_RADIUS * 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
                bricks = create_bricks()
                score, lives = 0, 3
            ball.center = (SCREEN_WIDTH / 2, paddle.y - BALL_RADIUS * 2)
            ball_speed_x, ball_speed_y = BALL_SPEED_INITIAL, -BALL_SPEED_INITIAL

        if not bricks:
            if end_screen(screen, clock, font, f"You Win! Score: {score}") == 'quit':
                return
            return # Return to menu on win

        screen.fill(BLACK)
        pygame.draw.rect(screen, PADDLE_COLOR, paddle)
        pygame.draw.ellipse(screen, BALL_COLOR, ball)
        for brick_info in bricks:
            pygame.draw.rect(screen, brick_info['color'], brick_info['rect'])

        draw_text(f"Score: {score}", font, WHITE, screen, 80, 20)
        draw_text(f"Lives: {lives}", font, WHITE, screen, SCREEN_WIDTH - 80, 20)

        pygame.display.flip()
        clock.tick(60)

def end_screen(screen, clock, font, message):
    while True:
        screen.fill(BLACK)
        draw_text(message, pygame.font.Font(None, 50), WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
        play_again_button = draw_text("Play Again", font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        quit_button = draw_text("Back to Menu", font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)

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

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()