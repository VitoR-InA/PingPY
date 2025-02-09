from _internal.GameClasses.Utils.RectUtils import RectUtils

import pygame as pg
import pymunk as pm

from random import randint
from typing import Tuple


class Grid:
    def __init__(self,
                 rect: pg.Rect | pg.typing.RectLike,
                 count: Tuple[int, int],
                 space: pm.Space):
        """
        Creates grid made from pymunk bodies

        Args:
            count (Tuple[int, int]): Defines the number of bodies in length and width
            space (pm.Space): Defines space where the Grid should be added
        """
        self.rect = RectUtils.index_rect(rect)
        
        self.cell_width = self.rect.width / count[0]
        self.cell_height = self.rect.height / count[1]
        grid_center = self.rect.center
        
        self.offset_x = grid_center[0] - (count[0] - 1) * self.cell_width / 2
        self.offset_y = grid_center[1] - (count[1] - 1) * self.cell_height / 2
        
        self.bodies = []
        self.shapes = []

        for x in range(count[0]):
            for y in range(count[1]):
                new_x = self.offset_x + x * self.cell_width
                new_y = self.offset_y + y * self.cell_height

                body = pm.Body(body_type=pm.Body.STATIC)
                body.position = (new_x, new_y)

                shape = pm.Poly.create_box(body, (self.cell_width, self.cell_height))
                shape.color = (randint(25, 255), randint(25, 255), randint(25, 255), 255)
                shape.elasticity = 1.003
                shape.collision_type = 2
                
                self.bodies.append(body)
                self.shapes.append(shape)
                space.add(body, shape)

    @classmethod
    def draw_test_grid(self,
                       rect: pg.Rect | pg.typing.RectLike,
                       count: Tuple[int, int],
                       surface: pg.Surface):
        """
        Draws test grid without space bodies

        Args:
            count (Tuple[int, int]): Defines the number of bodies in length and width
            surface (pg.Surface): _description_
        """
        self.rect = RectUtils.index_rect(rect)
        
        cell_width = self.rect.width / count[0]
        cell_height = self.rect.height / count[1]
        grid_center = self.rect.center
        
        offset_x = grid_center[0] - (count[0] - 1) * cell_width / 2
        offset_y = grid_center[1] - (count[1] - 1) * cell_height / 2
        
        for x in range(count[0]):
            for y in range(count[1]):
                new_x = offset_x + x * cell_width
                new_y = offset_y + y * cell_height
                
                pg.draw.rect(surface, "#FFFFFF", ((new_x - cell_width / 2, new_y - cell_height / 2),
                                                  (cell_width, cell_height)), 1)

    def draw(self, surface: pg.Surface):
        for num, body in enumerate(self.bodies):
            pg.draw.rect(surface, self.shapes[num].color, ((body.position[0] - self.cell_width / 2, body.position[1] - self.cell_height / 2),
                                                           (self.cell_width, self.cell_height + 1)))

    def remove(self, body: pm.Body, shape: pm.Shape):
        self.bodies.remove(body)
        self.shapes.remove(shape)

    def get_shapes(self):
        return self.shapes

    def get_bodies(self):
        return self.bodies