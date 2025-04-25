from core.entities import Entity
from core import typing

import pygame

import pymunk


class Player(Entity):
    def __init__(self, rect: typing.Union[typing.RectLike, pygame.Rect],
                 image: pygame.Surface,
                 health: int, speed: float):
        super().__init__(rect, elasticity = 1.005, body_type = pymunk.Body.KINEMATIC)

        self.original_image = image

        self.current_health = health
        self.max_health = health

        self.current_speed = speed

        self.rebuild()

    def set_image(self, new_image: pygame.Surface):
        self.original_image = new_image
        self.rebuild()

    def get_image(self): return self.original_image.copy()

    def set_max_health(self, new_max_health: int,
                       has_to_rebuild: bool = True):
        self.max_health = new_max_health

        if has_to_rebuild:
            self.rebuild()

    def rebuild(self):
        health_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        health_surface.fill((0, 0, 0, 0))

        self._health_surfaces = [health_surface]

        for current_health in range(self.max_health, 0, -1):
            health_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            health_surface.fill((0, 0, 0, 0))

            health_surface.blit(pygame.transform.smoothscale(self.original_image, self.rect.size))

            health_surface.fill((int(255 * (current_health / self.max_health)),
                                 int(255 * (1 - current_health / self.max_health)),
                                 0, 255), special_flags = pygame.BLEND_RGB_MULT)

            self._health_surfaces.append(health_surface)

    def update(self):
        super().update()

        self.image = self._health_surfaces[self.current_health]