import pygame


def blur(surface: pygame.Surface, factor: float):
    temp_surface = pygame.transform.smoothscale_by(surface, 1 / factor)
    return pygame.transform.smoothscale_by(temp_surface, 1 * factor)