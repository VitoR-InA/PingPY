import pygame as pg
import pymunk as pm

from typing import Tuple


class Ball:
    def __init__(self, mass: float,
                 position: Tuple[float, float],
                 radius: float,
                 color: Tuple[int, int, int, int],
                 space: pm.Space):
        self.mass = mass
        self.radius = radius
        self.moment = pm.moment_for_circle(self.mass, self.radius, 0)
        self.body = pm.Body(self.mass, self.moment)
        self.body.position = position
        self.shape = pm.Circle(self.body, radius)
        self.shape.collision_type = 1
        self.shape.elasticity = 1.01
        self.shape.friction = 0
        self.shape.color = color
        space.add(self.body, self.shape)
        
    def draw(self, surface):
        pg.draw.circle(surface, self.shape.color, self.body.position, self.radius)


class Box:
    def __init__(self,
                 rect: pg.Rect,
                 width: int,
                 space: pm.Space):
        self.shapes = []
        points = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft, rect.topleft]
        for i in range(len(points) - 1):
            segment = pm.Segment(space.static_body, points[i], points[i + 1], width)
            segment.elasticity = 1
            segment.friction = 0
            self.shapes.append(segment)
            space.add(segment)
            
    def get_shapes(self):
        return self.shapes


class Player:
    def __init__(self,
                 rect: pg.Rect,
                 color: Tuple[int, int, int, int],
                 space: pm.Space):
        self.rect = rect
        self.body = pm.Body(body_type=pm.Body.KINEMATIC)
        self.body.position = rect.topleft
        self.shape = pm.Poly.create_box(self.body, self.rect.size)
        self.shape.elasticity = 1
        self.shape.friction = 0
        self.shape.color = color
        space.add(self.body, self.shape)

    def draw(self, surface):
        pg.draw.rect(surface, self.shape.color, pg.Rect((self.body.position[0] - self.rect.size[0] / 2, self.body.position[1] - self.rect.size[1] / 2), self.rect.size))