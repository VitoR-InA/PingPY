import logging

import pygame as pg
import pymunk as pm

from random import randint
from typing import Tuple

logger = logging.getLogger(__name__)

class Grid:
    def __init__(self, space: pm.Space, rect: pg.Rect, count: Tuple[int, int]):
        self.body_width = rect.width / count[0]
        self.body_height = rect.height / count[1]
        grid_center = rect.center
        self.offset_x = grid_center[0] - (count[0] - 1) * self.body_width / 2
        self.offset_y = grid_center[1] - (count[1] - 1) * self.body_height / 2
        self.bodies = []
        self.shapes = []

        for x in range(count[0]):
            for y in range(count[1]):
                new_x = self.offset_x + x * self.body_width
                new_y = self.offset_y + y * self.body_height
                
                body = pm.Body(body_type=pm.Body.STATIC)
                body.position = (new_x, new_y)
                shape = pm.Poly.create_box(body, (self.body_width, self.body_height))
                shape.color = (randint(100, 255), randint(100, 255), randint(100, 255), 255)
                shape.elasticity = 1
                shape.collision_type = 2
                self.bodies.append(body)
                self.shapes.append(shape)
                space.add(body, shape)
        logger.info("New grid creation complete")

    def draw(self, surface: pg.Surface):
        for num, body in enumerate(self.bodies):
            pg.draw.rect(surface, self.shapes[num].color, pg.Rect((body.position[0] - self.body_width / 2, body.position[1] - self.body_height / 2), (self.body_width, self.body_height)))

    def get_shapes(self):
        return self.shapes

    def remove_shape(self, shape):
        try:
            self.bodies.pop(self.shapes.index(shape))
            self.shapes.pop(self.shapes.index(shape))
        except ValueError as exception:
            logger.warning(f"{shape} remove error:\n    {exception}")