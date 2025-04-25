from core.entities import Entity
from core import typing

import pygame

import pymunk


class GridBody(Entity):
    def __init__(self, rect: typing.Union[typing.RectLike, pygame.Rect], image: pygame.Surface):
        super().__init__(rect, elasticity = 1.005, collision_type = 2, body_type = pymunk.Body.STATIC)
        self.image = image