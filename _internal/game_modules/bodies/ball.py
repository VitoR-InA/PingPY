from math import cos, sin, radians

import pygame

import pymunk


class Ball:
    def __init__(self,
                 color: pygame,
                 center: pygame.typing.Point,
                 radius: float,
                 space: pymunk.Space):
        self.radius = radius
        self.angle = 90

        self.mass = 1
        self.moment = pymunk.moment_for_circle(self.mass, self.radius, 0)
        self.body = pymunk.Body(self.mass, self.moment)
        self.body.position = center

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.collision_type = 1
        self.shape.elasticity = 1.005
        self.shape.friction = 0
        self.shape.color = color

        space.add(self.body, self.shape)

    def draw_arrow(self, surface: pygame.Surface):
        "Draws arrow at given coordinates, defines ball direction"
        end_x = self.body.position[0] + 50 * cos(radians(self.angle))
        end_y = self.body.position[1] - 50 * sin(radians(self.angle))

        left_end_x = end_x + 25 * cos(radians(self.angle + 140))
        left_end_y = end_y - 25 * sin(radians(self.angle + 140))
        right_end_x = end_x + 25 * cos(radians(self.angle - 140))
        right_end_y = end_y - 25 * sin(radians(self.angle - 140))

        pygame.draw.line(surface, "#FFFFFF", (end_x, end_y), (left_end_x, left_end_y), 3)
        pygame.draw.line(surface, "#FFFFFF", (end_x, end_y), (right_end_x, right_end_y), 3)

        return (end_x - self.body.position[0], end_y - self.body.position[1])

    def set_angle(self, value: int = 90):
        self.angle = value

    def set_position(self, position):
        self.body.position = position
        
    def draw(self, surface):
        pygame.draw.circle(surface, self.shape.color, self.body.position, self.radius)