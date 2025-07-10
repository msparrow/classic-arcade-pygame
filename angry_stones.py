import pygame
import sys
import random
import scores
import pymunk

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (211, 0, 0)
BLUE = (135, 206, 250)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
GREEN = (0, 128, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (105, 105, 105)

# Multiplier for launch velocity
VELOCITY_MULTIPLIER = 10
WIN_LINE_Y = SCREEN_HEIGHT - 70

# --- Classes ---

class Stone:
    """Represents the stone to be launched, with enhanced drawing."""
    def __init__(self, space, position):
        self.radius = 15
        mass = 10
        inertia = pymunk.moment_for_circle(mass, 0, self.radius)
        self.body = pymunk.Body(mass, inertia)
        self.body.position = position
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = 0.6
        self.shape.friction = 0.9
        self.shape.collision_type = 1
        space.add(self.body, self.shape)
        self.is_flying = False

    def draw(self, screen):
        """Draws a more detailed stone."""
        pos = self.body.position
        if not all(map(lambda x: abs(x) < 1e9, pos)): return
        
        pygame.draw.circle(screen, GRAY, (int(pos.x), int(pos.y)), self.radius)
        pygame.draw.circle(screen, DARK_GRAY, (int(pos.x) + 3, int(pos.y) + 3), self.radius - 5)
        pygame.draw.circle(screen, BLACK, (int(pos.x), int(pos.y)), self.radius, 2)

class Block:
    """Represents a dynamic block."""
    def __init__(self, space, x, y, width, height):
        mass = 1
        size = (width, height)
        inertia = pymunk.moment_for_box(mass, size)
        self.body = pymunk.Body(mass, inertia)
        self.body.position = x + width / 2, y + height / 2
        self.shape = pymunk.Poly.create_box(self.body, size)
        self.shape.elasticity = 0.4
        self.shape.friction = 0.8
        space.add(self.body, self.shape)

    def draw(self, screen):
        points = self.shape.get_vertices()
        world_points = [p.rotated(self.body.angle) + self.body.position for p in points]
        pygame.draw.polygon(screen, BROWN, world_points)
        pygame.draw.polygon(screen, BLACK, world_points, 2)

class Target:
    """Represents the target ball."""
    def __init__(self, space, x, y):
        self.radius = 20
        mass = 5
        inertia = pymunk.moment_for_circle(mass, 0, self.radius)
        self.body = pymunk.Body(mass, inertia)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = 0.6
        self.shape.friction = 1.0
        self.shape.collision_type = 2
        space.add(self.body, self.shape)

    def draw(self, screen):
        pos = self.body.position
        pygame.draw.circle(screen, GREEN, (int(pos.x), int(pos.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(pos.x), int(pos.y)), self.radius, 2)

# --- Game Functions ---

def setup_level(space, level):
    """Sets up the game level with stable structures."""
    blocks = []
    targets = []
    
    ground_y = SCREEN_HEIGHT - 50

    if level == 1:
        # Simple tower on a platform
        blocks.append(Block(space, 600, ground_y - 20, 150, 20))
        blocks.append(Block(space, 650, ground_y - 40, 50, 20))
        targets.append(Target(space, 675, ground_y - 60))

    elif level == 2:
        # Small pyramid with two targets
        base_y = ground_y - 20
        blocks.append(Block(space, 600, base_y, 150, 20))
        blocks.append(Block(space, 625, base_y - 40, 100, 20))
        targets.append(Target(space, 675, base_y - 60))
        targets.append(Target(space, 620, base_y - 60))

    elif level == 3:
        # A bridge-like structure with a target on it
        support_height = 80
        support1_y = ground_y - support_height
        blocks.append(Block(space, 550, support1_y, 20, support_height))
        blocks.append(Block(space, 730, support1_y, 20, support_height))
        bridge_y = support1_y - 20
        blocks.append(Block(space, 570, bridge_y, 160, 20))
        targets.append(Target(space, 650, bridge_y - 20))

    elif level == 4:
        # A more complex tower with two targets
        base1_y = ground_y - 100
        blocks.append(Block(space, 600, base1_y, 20, 100))
        blocks.append(Block(space, 700, base1_y, 20, 100))
        layer1_y = base1_y - 20
        blocks.append(Block(space, 610, layer1_y, 100, 20))
        targets.append(Target(space, 660, layer1_y - 20))
        targets.append(Target(space, 630, ground_y - 20))

    elif level == 5:
        # A precarious stack with two targets
        stack_base_y = ground_y - 20
        block_width = 80
        block_height = 20
        for i in range(3):
            y_pos = stack_base_y - (i * block_height)
            x_pos = 650 - (block_width / 2)
            blocks.append(Block(space, x_pos, y_pos, block_width, block_height))
        targets.append(Target(space, 650, stack_base_y - 80))
        blocks.append(Block(space, 550, ground_y - 60, 80, 20))
        targets.append(Target(space, 590, ground_y - 80))

    elif level == 6:
        # Wall with three targets
        for i in range(3):
            blocks.append(Block(space, 550 + i * 80, ground_y - 100, 20, 100))
        for i in range(2):
            blocks.append(Block(space, 590 + i * 80, ground_y - 120, 80, 20))
        targets.append(Target(space, 570, ground_y - 140))
        targets.append(Target(space, 650, ground_y - 140))
        targets.append(Target(space, 730, ground_y - 140))

    elif level == 7:
        # Large pyramid with three targets
        base_y = ground_y - 20
        for i in range(3):
            blocks.append(Block(space, 550 + i * 40, base_y - i * 20, 200 - i * 80, 20))
        targets.append(Target(space, 650, base_y - 80))
        targets.append(Target(space, 600, base_y - 40))
        targets.append(Target(space, 700, base_y - 40))

    elif level == 8:
        # Complex structure with four targets
        blocks.append(Block(space, 550, ground_y - 80, 20, 80))
        blocks.append(Block(space, 750, ground_y - 80, 20, 80))
        blocks.append(Block(space, 570, ground_y - 100, 180, 20))
        blocks.append(Block(space, 650, ground_y - 160, 20, 60))
        targets.append(Target(space, 660, ground_y - 180))
        targets.append(Target(space, 580, ground_y - 120))
        targets.append(Target(space, 740, ground_y - 120))
        targets.append(Target(space, 660, ground_y - 20))

    elif level == 9:
        # Tall, unstable tower with three targets
        for i in range(5):
            blocks.append(Block(space, 650, ground_y - 20 - i * 20, 40, 20))
        targets.append(Target(space, 670, ground_y - 120))
        blocks.append(Block(space, 550, ground_y - 80, 80, 20))
        targets.append(Target(space, 590, ground_y - 100))
        blocks.append(Block(space, 750, ground_y - 80, 80, 20))
        targets.append(Target(space, 790, ground_y - 100))

    elif level == 10:
        # The final challenge with five targets
        blocks.append(Block(space, 500, ground_y - 120, 20, 120))
        blocks.append(Block(space, 800, ground_y - 120, 20, 120))
        blocks.append(Block(space, 520, ground_y - 140, 280, 20))
        blocks.append(Block(space, 650, ground_y - 200, 20, 60))
        targets.append(Target(space, 660, ground_y - 220))
        targets.append(Target(space, 530, ground_y - 160))
        targets.append(Target(space, 790, ground_y - 160))
        blocks.append(Block(space, 600, ground_y - 20, 80, 20))
        targets.append(Target(space, 640, ground_y - 40))
        blocks.append(Block(space, 700, ground_y - 20, 80, 20))
        targets.append(Target(space, 740, ground_y - 40))

    return blocks, targets

def draw_background(screen, level):
    if level == 1:
        # Original background
        screen.fill(BLUE)
        pygame.draw.circle(screen, (34, 139, 34), (200, SCREEN_HEIGHT), 150)
        pygame.draw.circle(screen, (34, 139, 34), (500, SCREEN_HEIGHT), 200)
        pygame.draw.rect(screen, BROWN, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
    elif level == 2:
        # Mountain background
        screen.fill((135, 206, 235))  # Sky blue
        # Sun
        pygame.draw.circle(screen, (255, 255, 0), (700, 80), 40)
        # Mountains
        pygame.draw.polygon(screen, (169, 169, 169), [(0, SCREEN_HEIGHT - 50), (200, 200), (350, 400), (500, 250), (600, 350), (800, 150), (800, SCREEN_HEIGHT-50)])
        pygame.draw.polygon(screen, (255, 250, 250), [(200, 200), (220, 220), (180, 220)]) # Snow cap
        pygame.draw.polygon(screen, (255, 250, 250), [(500, 250), (520, 270), (480, 270)]) # Snow cap
        pygame.draw.rect(screen, (34, 139, 34), (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)) # Grassy ground
    elif level == 3:
        # Lava background with volcano
        screen.fill((50, 50, 50)) # Dark sky
        # Volcano
        pygame.draw.polygon(screen, (40, 40, 40), [(300, SCREEN_HEIGHT - 50), (500, 100), (700, SCREEN_HEIGHT - 50)])
        # Lava pool
        pygame.draw.ellipse(screen, (255, 69, 0), (450, 120, 100, 30))
        # Lava flow
        pygame.draw.polygon(screen, (255, 69, 0), [(500, 135), (480, 250), (520, 250)])
        pygame.draw.rect(screen, (255, 69, 0), (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)) # Lava ground
    elif level == 4:
        # In the sky with clouds
        screen.fill((135, 206, 250)) # Sky blue
        # Sun
        pygame.draw.circle(screen, (255, 255, 0), (100, 100), 60)
        # Clouds
        for _ in range(5):
            pygame.draw.ellipse(screen, WHITE, (random.randint(0, SCREEN_WIDTH), random.randint(50, 250), random.randint(100, 200), random.randint(50, 100)))
        pygame.draw.rect(screen, (211, 211, 211), (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)) # Stone ground
    elif level == 5:
        # Farm background
        screen.fill((135, 206, 250)) # Sky blue
        # Sun
        pygame.draw.circle(screen, (255, 255, 0), (700, 80), 40)
        # Field
        pygame.draw.rect(screen, (244, 164, 96), (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        # Barn
        pygame.draw.rect(screen, (220, 20, 60), (100, SCREEN_HEIGHT - 250, 150, 150))
        pygame.draw.polygon(screen, (139, 0, 0), [(100, SCREEN_HEIGHT - 250), (250, SCREEN_HEIGHT - 250), (175, SCREEN_HEIGHT - 320)])
        # Fence
        for i in range(10):
            pygame.draw.rect(screen, (139, 69, 19), (50 + i * 80, SCREEN_HEIGHT - 120, 10, 70))
        pygame.draw.rect(screen, (139, 69, 19), (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 10))
    elif level == 6:
        # City background
        screen.fill((25, 25, 112)) # Midnight blue
        # Moon
        pygame.draw.circle(screen, (240, 230, 140), (700, 100), 50)
        # Buildings
        for i in range(5):
            pygame.draw.rect(screen, (105, 105, 105), (50 + i * 150, 200 + random.randint(-50, 50), 100, 400))
            for j in range(5):
                for k in range(3):
                    pygame.draw.rect(screen, (255, 255, 0), (60 + i * 150 + j * 20, 210 + k * 40, 10, 20))
        pygame.draw.rect(screen, (60, 60, 60), (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)) # Road
    elif level == 7:
        # Beach setting
        screen.fill((0, 191, 255)) # Ocean blue
        # Sun
        pygame.draw.circle(screen, (255, 215, 0), (100, 100), 60)
        # Sand
        pygame.draw.rect(screen, (238, 214, 175), (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        # Palm tree
        pygame.draw.rect(screen, (139, 69, 19), (600, SCREEN_HEIGHT - 250, 20, 150))
        for i in range(5):
            pygame.draw.polygon(screen, (34, 139, 34), [(610, SCREEN_HEIGHT - 250), (550 + i*20, SCREEN_HEIGHT - 280), (560+i*20, SCREEN_HEIGHT - 270)])
    elif level == 8:
        # Underwater background
        screen.fill((0, 105, 148)) # Deep blue
        # Bubbles
        for _ in range(20):
            pygame.draw.circle(screen, (173, 216, 230), (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)), random.randint(5, 15))
        # Fish
        for _ in range(5):
            pygame.draw.polygon(screen, (255, 165, 0), [(200, 200), (220, 180), (220, 220)])
        # Sandy bottom
        pygame.draw.rect(screen, (210, 180, 140), (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
    elif level == 9:
        # Forest background
        screen.fill((135, 206, 235)) # Day sky
        # Trees
        for i in range(6):
            pygame.draw.rect(screen, (139, 69, 19), (50 + i * 130, SCREEN_HEIGHT - 200, 30, 150))
            pygame.draw.circle(screen, (0, 100, 0), (65 + i * 130, SCREEN_HEIGHT - 200), 50)
        # Ground
        pygame.draw.rect(screen, (34, 139, 34), (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
    elif level == 10:
        # Space background
        screen.fill(BLACK)
        # Stars
        for _ in range(200):
            pygame.draw.circle(screen, WHITE, (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)), random.randint(1, 2))
        # Planets
        pygame.draw.circle(screen, (255, 0, 0), (100, 100), 50) # Red planet
        pygame.draw.circle(screen, (0, 0, 255), (700, 400), 80) # Blue planet
        # Moon surface
        pygame.draw.rect(screen, (128, 128, 128), (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))

def draw_dotted_line(screen, y, color):
    for x in range(0, SCREEN_WIDTH, 10):
        pygame.draw.line(screen, color, (x, y), (x + 5, y), 2)

def draw_slingshot(screen, slingshot_pos, stone_pos, is_aiming):
    """Draws a more detailed slingshot, with bands only when aiming."""
    fork_left = (slingshot_pos[0] - 20, slingshot_pos[1] - 30)
    fork_right = (slingshot_pos[0] + 20, slingshot_pos[1] - 30)
    base = (slingshot_pos[0], slingshot_pos[1] + 20)

    # Draw bands first if aiming, so they appear behind the slingshot
    if is_aiming:
        pygame.draw.line(screen, RED, fork_right, stone_pos, 4)
        pygame.draw.line(screen, RED, fork_left, stone_pos, 4)

    # Draw the wooden Y-shape
    pygame.draw.line(screen, DARK_BROWN, base, fork_left, 10)
    pygame.draw.line(screen, DARK_BROWN, base, fork_right, 10)

def run_game(screen, clock):
    from utils import draw_text
    # Instructions screen
    instructions = [
        "Click and drag the stone to launch it.",
        "The goal is to knock the green ball off the platform.",
        "The ball must fall below the red dotted line to win.",
        "You have a limited number of stones.",
        "",
        "Press any key or click to start."
    ]
    show_instructions = True
    while show_instructions:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                show_instructions = False
        screen.fill(BLACK)
        title_font = pygame.font.Font(None, 60)
        instruction_font = pygame.font.Font(None, 30)
        draw_text("Angry Stones", title_font, WHITE, screen, SCREEN_WIDTH / 2, 100)
        y_offset = 200
        for line in instructions:
            draw_text(line, instruction_font, WHITE, screen, SCREEN_WIDTH / 2, y_offset)
            y_offset += 40
        pygame.display.flip()
        clock.tick(60)

    pygame.display.set_caption("Angry Stones - Physics Edition")
    
    space = pymunk.Space()
    space.gravity = (0, 500)
    space.sleep_time_threshold = 0.5

    ground_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    ground_shape = pymunk.Segment(ground_body, (0, SCREEN_HEIGHT - 50), (SCREEN_WIDTH, SCREEN_HEIGHT - 50), 5)
    ground_shape.friction = 1.0
    space.add(ground_body, ground_shape)

    slingshot_pos = (160, SCREEN_HEIGHT - 120)
    
    level = 1
    max_levels = 10
    stones_per_level = 5

    def clear_level_objects(space, objects):
        for obj in objects:
            if obj.body in space.bodies:
                space.remove(obj.body, obj.shape)

    def create_new_stone():
        stone = Stone(space, slingshot_pos)
        stone.body.sleep()
        return stone

    blocks, targets = setup_level(space, level)
    stone = create_new_stone()
    level_objects = blocks + targets + [stone]
    
    is_aiming = False
    score = 0
    stones_left = stones_per_level
    game_over = False
    win = False
    win_condition_met = False
    win_timer = None
    font = pygame.font.Font(None, 36)
    
    slingshot_grab_area = pygame.Rect(slingshot_pos[0] - 30, slingshot_pos[1] - 30, 60, 60)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return

            if not game_over and not win and not stone.is_flying and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if slingshot_grab_area.collidepoint(mouse_pos):
                    is_aiming = True

            if is_aiming and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                is_aiming = False
                
                pull_vector = (slingshot_pos[0] - mouse_pos[0], slingshot_pos[1] - mouse_pos[1])
                
                stone.body.activate()
                stone.body.velocity = (pull_vector[0] * VELOCITY_MULTIPLIER, pull_vector[1] * VELOCITY_MULTIPLIER)
                
                stone.is_flying = True
                stones_left -= 1

        # --- Update ---
        space.step(1.0 / 60.0)

        if stone.is_flying and (stone.body.position.y > SCREEN_HEIGHT or stone.body.is_sleeping):
            if stones_left > 0 and not win and not win_condition_met:
                space.remove(stone.body, stone.shape)
                stone = create_new_stone()
                level_objects.append(stone)
            elif not win and not win_condition_met:
                game_over = True

        # --- Win/Lose Condition Check ---
        if not win_condition_met and targets and all((t.body.position.y + t.radius) > WIN_LINE_Y for t in targets):
            win_condition_met = True
            win_timer = pygame.time.get_ticks()

        if win_condition_met and not win:
            if pygame.time.get_ticks() - win_timer > 1000:
                win = True
                score += stones_left * 10
                scores.save_score("Angry Stones", score)
                level += 1
                if level > max_levels:
                    game_over = True # Game finished
                else:
                    # Next level
                    clear_level_objects(space, level_objects)
                    
                    # Display level completed message
                    screen.fill(BLACK)
                    level_completed_font = pygame.font.Font(None, 60)
                    draw_text(f"Level {level - 1} Completed!", level_completed_font, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                    pygame.display.flip()
                    pygame.time.wait(2000)

                    blocks, targets = setup_level(space, level)
                    stone = create_new_stone()
                    level_objects = blocks + targets + [stone]
                    stones_left = stones_per_level
                    win = False
                    win_condition_met = False


        if not win and not game_over and stones_left <= 0 and stone.body.is_sleeping and not win_condition_met:
            game_over = True
            scores.save_score("Angry Stones", score)

        # --- Drawing ---
        draw_background(screen, level)
        for b in blocks:
            b.draw(screen)
        for t in targets:
            t.draw(screen)
        
        visual_stone_pos = mouse_pos if is_aiming else stone.body.position
        draw_slingshot(screen, slingshot_pos, visual_stone_pos, is_aiming)
        
        if not stone.is_flying:
            stone_draw_pos = mouse_pos if is_aiming else slingshot_pos
            pygame.draw.circle(screen, GRAY, stone_draw_pos, 15)
            pygame.draw.circle(screen, DARK_GRAY, (stone_draw_pos[0] + 3, stone_draw_pos[1] + 3), 10)
            pygame.draw.circle(screen, BLACK, stone_draw_pos, 15, 2)
        else:
            stone.draw(screen)

        draw_dotted_line(screen, WIN_LINE_Y, RED)

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        stones_text = font.render(f"Stones: {stones_left}", True, WHITE)
        screen.blit(stones_text, (10, 50))
        level_text = font.render(f"Level: {level if level <= max_levels else max_levels}", True, WHITE)
        screen.blit(level_text, (10, 90))

        if game_over:
            message = "You Win!" if win and level > max_levels else "Game Over"
            win_text = font.render(message, True, WHITE)
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(win_text, win_rect)
            pygame.display.flip()
            pygame.time.wait(2000)
            return

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    run_game(screen, clock)
    pygame.quit()
    sys.exit()
