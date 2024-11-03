import logging

import pygame as pg
import pymunk as pm

from typing import Tuple

logger = logging.getLogger(__name__)

class Ball:
    def __init__(self, mass: float, position: Tuple[float, float], radius: float, color: Tuple[int, int, int, int], space: pm.Space):
        self.mass = mass
        self.radius = radius
        self.moment = pm.moment_for_circle(self.mass, self.radius, 0)
        self.body = pm.Body(self.mass, self.moment)
        self.body.position = position
        self.shape = pm.Circle(self.body, radius)
        self.shape.collision_type = 1
        self.shape.elasticity = 1.005
        self.shape.friction = 0
        self.shape.color = color
        space.add(self.body, self.shape)
        
    def draw(self, surface):
        pg.draw.circle(surface, self.shape.color, self.body.position, self.radius)

class Player:
    def __init__(self, rect: pg.Rect, color: Tuple[int, int, int, int], space: pm.Space):
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

class Wall:
    def __init__(self, a: Tuple[float, float], b: Tuple[float, float], radius: float, space: pm.Space):
        self.segment = pm.Segment(space.static_body, a, b, radius)
        self.segment.elasticity = 1
        self.segment.friction = 0
        space.add(self.segment)