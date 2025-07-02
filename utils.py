"""
Shared utility functions for the Pygame Arcade.

This module contains functions that are used by multiple games, such as drawing text,
- handling menus (pause, settings), and screen transitions.
"""

import pygame
import random

# --- Particle System ---
class Particle:
    def __init__(self, x, y, color, size, life, dx, dy):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.life = life
        self.dx = dx
        self.dy = dy

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        if self.size > 0:
            self.size -= 0.1

    def draw(self, screen):
        if self.life > 0 and self.size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

def create_explosion(particles, x, y, color, count=20):
    for _ in range(count):
        dx = random.uniform(-4, 4)
        dy = random.uniform(-4, 4)
        size = random.uniform(2, 6)
        life = random.randint(20, 40)
        particles.append(Particle(x, y, color, size, life, dx, dy))

# --- Screen Shake ---
class ScreenShaker:
    def __init__(self, intensity, duration):
        self.intensity = intensity
        self.duration = duration
        self.timer = 0

    def shake(self):
        if self.timer < self.duration:
            self.timer += 1
            offset_x = random.randint(-self.intensity, self.intensity)
            offset_y = random.randint(-self.intensity, self.intensity)
            return (offset_x, offset_y)
        return (0, 0)

def draw_text(text, font, color, surface, x, y, center=True):
    """
    Helper function to draw text on a surface.

    Args:
        text (str): The text to draw.
        font (pygame.font.Font): The font to use.
        color (tuple): The color of the text.
        surface (pygame.Surface): The surface to draw on.
        x (int): The x-coordinate for the text position.
        y (int): The y-coordinate for the text position.
        center (bool, optional): Whether to center the text at the given coordinates. Defaults to True.

    Returns:
        pygame.Rect: The rectangle enclosing the drawn text.
    """
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)
    return textrect


def fade_transition(screen, clock, fade_out=True, duration=500):
    """
    Performs a fade-in or fade-out transition.

    Args:
        screen (pygame.Surface): The Pygame screen surface.
        clock (pygame.time.Clock): The Pygame clock object.
        fade_out (bool, optional): True for fade out (to black), False for fade in (from black). Defaults to True.
        duration (int, optional): Duration of the fade in milliseconds. Defaults to 500.
    """
    start_time = pygame.time.get_ticks()
    original_surface = screen.copy()

    while True:
        elapsed_time = pygame.time.get_ticks() - start_time
        alpha = int(255 * (elapsed_time / duration))

        if fade_out:
            alpha = 255 - alpha

        if alpha < 0: alpha = 0
        if alpha > 255: alpha = 255

        screen.blit(original_surface, (0, 0))
        fade_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, alpha))
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()

        if elapsed_time > duration:
            break
        clock.tick(60)

def pause_menu(screen, clock, game_width, game_height):
    """
    Displays a pause menu and waits for user input.

    Args:
        screen (pygame.Surface): The Pygame screen surface.
        clock (pygame.time.Clock): The Pygame clock object.
        game_width (int): The width of the game screen.
        game_height (int): The height of the game screen.

    Returns:
        str: The action selected by the user ('resume' or 'quit').
    """
    overlay = pygame.Surface((game_width, game_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    # Fonts and colors for the pause menu.
    title_font = pygame.font.Font(None, 80)
    button_font = pygame.font.Font(None, 40)
    TEXT_COLOR = (255, 255, 255)
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)

    draw_text("PAUSED", title_font, TEXT_COLOR, screen, game_width / 2, game_height / 2 - 100)

    # Define button properties.
    button_width = 250
    button_height = 60
    button_spacing = 20
    resume_y = game_height / 2 + 20
    quit_y = resume_y + button_height + button_spacing

    resume_rect = pygame.Rect(game_width / 2 - button_width / 2, resume_y, button_width, button_height)
    quit_rect = pygame.Rect(game_width / 2 - button_width / 2, quit_y, button_width, button_height)

    buttons = [
        {"text": "Resume (P)", "rect": resume_rect, "action": "resume"},
        {"text": "Quit to Menu (Q)", "rect": quit_rect, "action": "quit"}
    ]

    pygame.display.flip()

    # Main loop for the pause menu.
    while True:
        mouse_pos = pygame.mouse.get_pos()
        # Event handling.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return 'resume'
                if event.key == pygame.K_q:
                    return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        return button["action"]

        # Redraw buttons to show hover effects.
        screen.blit(overlay, (0, 0))
        draw_text("PAUSED", title_font, TEXT_COLOR, screen, game_width / 2, game_height / 2 - 100)

        for button in buttons:
            current_button_color = BUTTON_HOVER_COLOR if button["rect"].collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, current_button_color, button["rect"], border_radius=10)
            pygame.draw.rect(screen, BORDER_COLOR, button["rect"], 2, border_radius=10)
            draw_text(button["text"], button_font, TEXT_COLOR, screen, button["rect"].centerx, button["rect"].centery)

        pygame.display.flip()
        clock.tick(30)

def settings_menu(screen, clock, game_width, game_height, initial_volume):
    """
    Displays a settings menu for music volume.

    Args:
        screen (pygame.Surface): The Pygame screen surface.
        clock (pygame.time.Clock): The Pygame clock object.
        game_width (int): The width of the game screen.
        game_height (int): The height of the game screen.
        initial_volume (float): The current music volume (0.0 to 1.0).

    Returns:
        tuple: A tuple containing the new volume and a status ('resume' or 'quit').
    """
    overlay = pygame.Surface((game_width, game_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))

    # Fonts and colors for the settings menu.
    title_font = pygame.font.Font(None, 80)
    label_font = pygame.font.Font(None, 40)
    button_font = pygame.font.Font(None, 40)
    TEXT_COLOR = (255, 255, 255)
    BUTTON_COLOR = (50, 50, 50)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BORDER_COLOR = (150, 150, 150)
    SLIDER_BAR_COLOR = (100, 100, 100)
    SLIDER_FILL_COLOR = (0, 200, 0)
    HANDLE_COLOR = (255, 255, 255)

    # Volume slider properties.
    slider_width = 300
    slider_height = 20
    slider_x = game_width / 2 - slider_width / 2
    slider_y = game_height / 2
    handle_radius = 15

    current_volume = initial_volume
    dragging_handle = False

    # Back button properties.
    button_width = 250
    button_height = 60
    back_button_rect = pygame.Rect(game_width / 2 - button_width / 2, game_height / 2 + 100, button_width, button_height)

    # Main loop for the settings menu.
    while True:
        mouse_pos = pygame.mouse.get_pos()
        # Redraw the overlay and elements each frame.
        screen.blit(overlay, (0, 0))
        draw_text("SETTINGS", title_font, TEXT_COLOR, screen, game_width / 2, game_height / 2 - 150)
        draw_text("Music Volume", label_font, TEXT_COLOR, screen, game_width / 2, slider_y - 40)

        # Draw the volume slider.
        pygame.draw.rect(screen, SLIDER_BAR_COLOR, (slider_x, slider_y, slider_width, slider_height), border_radius=5)
        fill_width = int(current_volume * slider_width)
        pygame.draw.rect(screen, SLIDER_FILL_COLOR, (slider_x, slider_y, fill_width, slider_height), border_radius=5)

        # Draw the slider handle.
        handle_x = slider_x + current_volume * slider_width
        handle_rect = pygame.Rect(handle_x - handle_radius, slider_y + slider_height / 2 - handle_radius, handle_radius * 2, handle_radius * 2)
        pygame.draw.circle(screen, HANDLE_COLOR, (int(handle_x), int(slider_y + slider_height / 2)), handle_radius)
        pygame.draw.circle(screen, BORDER_COLOR, (int(handle_x), int(slider_y + slider_height / 2)), handle_radius, 2)

        # Display the current volume percentage.
        volume_percent_text = label_font.render(f"{int(current_volume * 100)}%", True, TEXT_COLOR)
        screen.blit(volume_percent_text, (slider_x + slider_width + 20, slider_y - 5))

        # Draw the Back button.
        current_button_color = BUTTON_HOVER_COLOR if back_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, current_button_color, back_button_rect, border_radius=10)
        pygame.draw.rect(screen, BORDER_COLOR, back_button_rect, 2, border_radius=10)
        draw_text("Back (Esc)", button_font, TEXT_COLOR, screen, back_button_rect.centerx, back_button_rect.centery)

        # Event handling.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return current_volume, 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if handle_rect.collidepoint(event.pos):
                    dragging_handle = True
                elif pygame.Rect(slider_x, slider_y, slider_width, slider_height).collidepoint(event.pos):
                    current_volume = (event.pos[0] - slider_x) / slider_width
                    current_volume = max(0.0, min(1.0, current_volume))
                    pygame.mixer.music.set_volume(current_volume)
                if back_button_rect.collidepoint(event.pos):
                    return current_volume, 'resume'
            if event.type == pygame.MOUSEBUTTONUP:
                dragging_handle = False
            if event.type == pygame.MOUSEMOTION and dragging_handle:
                current_volume = (event.pos[0] - slider_x) / slider_width
                current_volume = max(0.0, min(1.0, current_volume))
                pygame.mixer.music.set_volume(_volume)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return current_volume, 'resume'
                if event.key == pygame.K_LEFT:
                    current_volume = max(0.0, current_volume - 0.05)
                    pygame.mixer.music.set_volume(current_volume)
                if event.key == pygame.K_RIGHT:
                    current_volume = min(1.0, current_volume + 0.05)
                    pygame.mixer.music.set_volume(current_volume)

        pygame.display.flip()
        clock.tick(30)
