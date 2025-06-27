import pygame
import sys
import random

# --- Initialization ---
pygame.init()

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BLACK, WHITE, GREEN, RED = (0, 0, 0), (255, 255, 255), (0, 255, 0), (255, 0, 0)

PLAYER_SIZE, PLAYER_SPEED = 50, 5
BULLET_WIDTH, BULLET_HEIGHT, BULLET_SPEED = 5, 15, 10
ALIEN_ROWS, ALIEN_COLS = 5, 11
ALIEN_SIZE, ALIEN_GAP = 40, 10
ALIEN_SPEED_X, ALIEN_SPEED_Y = 1, 20
ALIEN_FIRE_RATE = 100

def create_aliens():
    aliens = []
    for row in range(ALIEN_ROWS):
        for col in range(ALIEN_COLS):
            x = col * (ALIEN_SIZE + ALIEN_GAP) + 50
            y = row * (ALIEN_SIZE + ALIEN_GAP) + 50
            aliens.append(pygame.Rect(x, y, ALIEN_SIZE, ALIEN_SIZE))
    return aliens

def draw_text(text, font, color, surface, x, y, center=True):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)
    return textrect

def run_game(screen, clock):
    pygame.display.set_caption("Space Invaders")
    font = pygame.font.Font(None, 36)
    player = pygame.Rect(SCREEN_WIDTH / 2 - PLAYER_SIZE / 2, SCREEN_HEIGHT - 70, PLAYER_SIZE, PLAYER_SIZE)
    player_bullets, aliens, alien_bullets = [], create_aliens(), []
    alien_direction, score, lives = 1, 0, 3

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Allows quitting from the game window
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and len(player_bullets) < 3:
                    bullet = pygame.Rect(player.centerx - BULLET_WIDTH / 2, player.top, BULLET_WIDTH, BULLET_HEIGHT)
                    player_bullets.append(bullet)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0: player.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and player.right < SCREEN_WIDTH: player.x += PLAYER_SPEED

        for bullet in player_bullets[:]:
            bullet.y -= BULLET_SPEED
            if bullet.bottom < 0: player_bullets.remove(bullet)

        for bullet in alien_bullets[:]:
            bullet.y += BULLET_SPEED
            if bullet.top > SCREEN_HEIGHT: alien_bullets.remove(bullet)

        move_down = False
        for alien in aliens:
            alien.x += alien_direction * ALIEN_SPEED_X
            if alien.right >= SCREEN_WIDTH or alien.left <= 0: move_down = True
        if move_down:
            alien_direction *= -1
            for alien in aliens: alien.y += ALIEN_SPEED_Y

        if random.randint(1, ALIEN_FIRE_RATE) == 1 and aliens:
            shooter = random.choice(aliens)
            bullet = pygame.Rect(shooter.centerx - BULLET_WIDTH / 2, shooter.bottom, BULLET_WIDTH, BULLET_HEIGHT)
            alien_bullets.append(bullet)

        for bullet in player_bullets[:]:
            for alien in aliens[:]:
                if bullet.colliderect(alien):
                    player_bullets.remove(bullet)
                    aliens.remove(alien)
                    score += 100
                    break

        for bullet in alien_bullets[:]:
            if bullet.colliderect(player):
                alien_bullets.remove(bullet)
                lives -= 1
                if lives <= 0:
                    if end_screen(screen, clock, font, f"Game Over! Score: {score}") == 'quit':
                        return
                    # Restart
                    player = pygame.Rect(SCREEN_WIDTH / 2 - PLAYER_SIZE / 2, SCREEN_HEIGHT - 70, PLAYER_SIZE, PLAYER_SIZE)
                    player_bullets, aliens, alien_bullets = [], create_aliens(), []
                    alien_direction, score, lives = 1, 0, 3

        if not aliens:
            if end_screen(screen, clock, font, f"You Win! Score: {score}") == 'quit':
                return
            # Restart
            player = pygame.Rect(SCREEN_WIDTH / 2 - PLAYER_SIZE / 2, SCREEN_HEIGHT - 70, PLAYER_SIZE, PLAYER_SIZE)
            player_bullets, aliens, alien_bullets = [], create_aliens(), []
            alien_direction, score, lives = 1, 0, 3
        for alien in aliens:
            if alien.bottom >= player.top:
                if end_screen(screen, clock, font, f"Game Over! Score: {score}") == 'quit':
                    return

        screen.fill(BLACK)
        pygame.draw.rect(screen, GREEN, player)
        for bullet in player_bullets: pygame.draw.rect(screen, WHITE, bullet)
        for alien in aliens: pygame.draw.rect(screen, RED, alien)
        for bullet in alien_bullets: pygame.draw.rect(screen, RED, bullet)

        draw_text(f"Score: {score}", font, WHITE, screen, 100, 20)
        draw_text(f"Lives: {lives}", font, WHITE, screen, SCREEN_WIDTH - 100, 20)

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