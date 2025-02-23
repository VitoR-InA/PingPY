import pygame
from pygame import Rect

import pymunk

from itertools import product

from random import randint

import typing


class Grid:
    def __init__(self,
                 rect: Rect,
                 count: pygame.typing.Point):
        """
        Creates grid made from pymunk bodies

        Args:
            count (pygame.typing.Point): Defines the number of bodies in length and width
            space (pymunk.Space): Defines space where the Grid should be added
        """
        self.rect = rect
        
        self.cell_width = self.rect.width / count[0]
        self.cell_height = self.rect.height / count[1]
        grid_center = self.rect.center
        
        self.offset_x = grid_center[0] - (count[0] - 1) * self.cell_width / 2
        self.offset_y = grid_center[1] - (count[1] - 1) * self.cell_height / 2
        
        self.bodies: typing.List[pymunk.Body] = []
        self.shapes: typing.List[pymunk.Shape] = []

        for x, y in product(range(count[0]), range(count[1])):
            new_x = self.offset_x + x * self.cell_width
            new_y = self.offset_y + y * self.cell_height

            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = (new_x, new_y)

            shape = pymunk.Poly.create_box(body, (self.cell_width, self.cell_height))
            shape.color = (randint(25, 255), randint(25, 255), randint(25, 255), 255)
            shape.elasticity = 1.005
            shape.collision_type = 2
            
            self.bodies.append(body)
            self.shapes.append(shape)

    @classmethod
    def draw_preview(self,
                     rect: Rect,
                     count: pygame.typing.Point,
                     surface: pygame.Surface):
        """
        Draws test grid without space bodies

        Args:
            count (pygame.typing.Point): Defines the number of bodies in length and width
            surface (pygame.Surface): _description_
        """
        self.rect = rect
        
        cell_width = self.rect.width / count[0]
        cell_height = self.rect.height / count[1]
        grid_center = self.rect.center
        
        offset_x = grid_center[0] - (count[0] - 1) * cell_width / 2
        offset_y = grid_center[1] - (count[1] - 1) * cell_height / 2
        
        for x in range(count[0]):
            for y in range(count[1]):
                new_x = offset_x + x * cell_width
                new_y = offset_y + y * cell_height
                
                pygame.draw.rect(surface, "#FFFFFF", ((new_x - cell_width / 2, new_y - cell_height / 2),
                                                  (cell_width, cell_height)), 1)

    def draw(self, surface: pygame.Surface):
        for num, body in enumerate(self.bodies):
            pygame.draw.rect(surface, self.shapes[num].color, ((body.position[0] - self.cell_width / 2, body.position[1] - self.cell_height / 2),
                                                           (self.cell_width, self.cell_height + 1)))

    def clear(self):
        for body in self.bodies:
            for shape in body.shapes:
                if shape in body.space.shapes:
                    body.space.remove(shape)
            body.space.remove(body)
        self.bodies.clear()
        self.shapes.clear()

    def remove(self, *objs):
        for obj in objs:
            if isinstance(obj, pymunk.Body) and obj in self.bodies: self.bodies.remove(obj)
            elif isinstance(obj, pymunk.Shape) and obj in self.shapes: self.shapes.remove(obj)