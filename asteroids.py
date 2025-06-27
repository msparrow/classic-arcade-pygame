import pygame
import sys
import random
import math

# --- Initialization ---
pygame.init()

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BLACK, WHITE = (0, 0, 0), (255, 255, 255)

PLAYER_SIZE, PLAYER_ROTATION_SPEED, PLAYER_ACCELERATION, PLAYER_FRICTION = 20, 5, 0.2, 0.99
BULLET_SPEED, BULLET_LIFESPAN = 10, 40
ASTEROID_SPEED, ASTEROID_INITIAL_COUNT = 2, 5

class Player:
    def __init__(self):
        self.pos = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.vel = pygame.Vector2(0, 0)
        self.angle = 0

    def update(self):
        self.pos += self.vel
        self.vel *= PLAYER_FRICTION
        if self.pos.x > SCREEN_WIDTH: self.pos.x = 0
        if self.pos.x < 0: self.pos.x = SCREEN_WIDTH
        if self.pos.y > SCREEN_HEIGHT: self.pos.y = 0
        if self.pos.y < 0: self.pos.y = SCREEN_HEIGHT

    def draw(self, surface):
        angle_rad = math.radians(self.angle)
        points = [
            (self.pos.x + PLAYER_SIZE * math.cos(angle_rad), self.pos.y - PLAYER_SIZE * math.sin(angle_rad)),
            (self.pos.x + PLAYER_SIZE * math.cos(angle_rad + 2.5) / 2, self.pos.y - PLAYER_SIZE * math.sin(angle_rad + 2.5) / 2),
            (self.pos.x + PLAYER_SIZE * math.cos(angle_rad - 2.5) / 2, self.pos.y - PLAYER_SIZE * math.sin(angle_rad - 2.5) / 2)
        ]
        pygame.draw.polygon(surface, WHITE, points, 1)

class Bullet:
    def __init__(self, pos, angle):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(BULLET_SPEED, 0).rotate(-angle)
        self.lifespan = BULLET_LIFESPAN

    def update(self):
        self.pos += self.vel
        self.lifespan -= 1

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.pos.x), int(self.pos.y)), 2)

class Asteroid:
    def __init__(self, pos=None, size=3):
        self.pos = pygame.Vector2(pos) if pos else pygame.Vector2(random.randrange(SCREEN_WIDTH), random.randrange(SCREEN_HEIGHT))
        self.vel = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * ASTEROID_SPEED
        self.size = size
        self.radius = self.size * 15

    def update(self):
        self.pos += self.vel
        if self.pos.x > SCREEN_WIDTH + self.radius: self.pos.x = -self.radius
        if self.pos.x < -self.radius: self.pos.x = SCREEN_WIDTH + self.radius
        if self.pos.y > SCREEN_HEIGHT + self.radius: self.pos.y = -self.radius
        if self.pos.y < -self.radius: self.pos.y = SCREEN_HEIGHT + self.radius

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.pos.x), int(self.pos.y)), self.radius, 1)

def run_game(screen, clock):
    pygame.display.set_caption("Asteroids")
    font = pygame.font.Font(None, 36)
    player = Player()
    bullets, asteroids = [], [Asteroid() for _ in range(ASTEROID_INITIAL_COUNT)]
    score, game_over = 0, False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Allows quitting from the game window
                return
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_SPACE and len(bullets) < 5:
                    bullets.append(Bullet(player.pos, player.angle))

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: player.angle += PLAYER_ROTATION_SPEED
            if keys[pygame.K_RIGHT]: player.angle -= PLAYER_ROTATION_SPEED
            if keys[pygame.K_UP]: player.vel += pygame.Vector2(PLAYER_ACCELERATION, 0).rotate(-player.angle)

            player.update()
            for b in bullets[:]:
                b.update()
                if b.lifespan <= 0: bullets.remove(b)
            for a in asteroids: a.update()

            for b in bullets[:]:
                for a in asteroids[:]:
                    if b.pos.distance_to(a.pos) < a.radius:
                        bullets.remove(b)
                        asteroids.remove(a)
                        score += 10 * (4 - a.size)
                        if a.size > 1:
                            asteroids.extend([Asteroid(a.pos, a.size - 1), Asteroid(a.pos, a.size - 1)])
                        break

            for a in asteroids:
                if player.pos.distance_to(a.pos) < a.radius + PLAYER_SIZE / 2:
                    game_over = True

        screen.fill(BLACK)
        player.draw(screen)
        for b in bullets: b.draw(screen)
        for a in asteroids: a.draw(screen)

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if game_over:
            if end_screen(screen, clock, font, f"Game Over! Score: {score}") == 'quit':
                return
            # Restart game
            player = Player()
            bullets, asteroids = [], [Asteroid() for _ in range(ASTEROID_INITIAL_COUNT)]
            score, game_over = 0, False
        if not asteroids:
            if end_screen(screen, clock, font, f"You Win! Score: {score}") == 'quit':
                return
            # Restart game
            player = Player()
            bullets, asteroids = [], [Asteroid() for _ in range(ASTEROID_INITIAL_COUNT)]
            score, game_over = 0, False

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
                if play_again_button.collidepoint(event.pos): return 'play_again'
                if quit_button.collidepoint(event.pos): return 'quit'

        pygame.display.flip()
        clock.tick(15)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)
    return textrect

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()