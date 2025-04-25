from core.entities import Entity
from core import typing

import pygame

import pymunk


class Ball(Entity):
    def __init__(self, rect: typing.Union[typing.RectLike, pygame.Rect], image: pygame.Surface):
        super().__init__(rect, mass = 1, elasticity = 1.005, collision_type = 1, body_type = pymunk.Body.DYNAMIC)

        self.original_image = image

        self.rotation_lock = True
        self.speed_lock = False
        
        self.rebuild()

    def get_image(self): return self.original_image.copy()

    def rebuild(self):
        self.image = pygame.transform.smoothscale(self.original_image, self.rect.size)

    def set_image(self, new_image: pygame.Surface):
        self.original_image = new_image
        self.rebuild()

    def update(self):
        super().update()

        if self.rotation_lock:
            self.body.angle = 0

        # if self.speed_lock:
        #     self.body.velocity = [min(self.speed_lock, vel) for vel in self.body.velocity]