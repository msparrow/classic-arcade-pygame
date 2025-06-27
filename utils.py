"""
Shared utility functions for the Pygame Arcade.
"""
import pygame

def draw_text(text, font, color, surface, x, y, center=True):
    """Helper function to draw text on a surface."""
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)
    return textrect