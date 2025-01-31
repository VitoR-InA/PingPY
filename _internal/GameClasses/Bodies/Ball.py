from _internal.GameClasses.Utils.ColorUtils import ColorUtils

from math import cos, sin, radians

import pygame as pg

import pymunk as pm


class Ball:
    def __init__(self,
                 color: pg.typing.ColorLike,
                 center: pg.typing.Point,
                 radius: float,
                 space: pm.Space):
        self.radius = radius
        self.angle = 90

        self.mass = 1
        self.moment = pm.moment_for_circle(self.mass, self.radius, 0)
        self.body = pm.Body(self.mass, self.moment)
        self.body.position = center

        self.shape = pm.Circle(self.body, radius)
        self.shape.collision_type = 1
        self.shape.elasticity = 1.001
        self.shape.friction = 0
        self.shape.color = ColorUtils.index_color(color)

        space.add(self.body, self.shape)

    def draw_arrow(self, surface: pg.Surface):
        "Draws arrow at given coordinates, defines ball direction"
        self.end_x = self.body.position[0] + 50 * cos(radians(self.angle))
        self.end_y = self.body.position[1] - 50 * sin(radians(self.angle))

        left_end_x = self.end_x + 25 * cos(radians(self.angle + 140))
        left_end_y = self.end_y - 25 * sin(radians(self.angle + 140))
        right_end_x = self.end_x + 25 * cos(radians(self.angle - 140))
        right_end_y = self.end_y - 25 * sin(radians(self.angle - 140))

        pg.draw.line(surface, "#FFFFFF", (self.end_x, self.end_y), (left_end_x, left_end_y), 3)
        pg.draw.line(surface, "#FFFFFF", (self.end_x, self.end_y), (right_end_x, right_end_y), 3)

        return (self.end_x - self.body.position[0], self.end_y - self.body.position[1])

    def set_angle(self, value: int = 90):
        self.angle = value

    def set_position(self, position):
        self.body.position = position
        
    def draw(self, surface):
        pg.draw.circle(surface, self.shape.color, self.body.position, self.radius)