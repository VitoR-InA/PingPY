from math import cos, sin

import pygame
from pygame import Rect

import pymunk


class Ball(pymunk.Body):
    def __init__(self, color: pygame.Color,
                 center: pygame.typing.Point,
                 radius: float):
        moment = pymunk.moment_for_circle(10, radius, 0)
        super().__init__(10, moment)
        self.set_position(center)

        self.shape = pymunk.Circle(self, radius)
        self.shape.collision_type = 1
        self.shape.elasticity = 1.005
        self.shape.color = color

    def draw_direction_arrow(self, surface: pygame.Surface):
        size_factor = self.shape.radius / 10

        arrow_length = round(50 * size_factor)
        arrow_sides_length = round(25 * size_factor)
        line_width = round(3 * size_factor)

        end_x = self.position.x + arrow_length * cos(self.angle)
        end_y = self.position.y + arrow_length * sin(self.angle)

        left_dx = arrow_sides_length * cos(self.angle + 2.4455)
        left_dy = arrow_sides_length * sin(self.angle + 2.4455)
        left_end = (end_x + left_dx, end_y + left_dy)

        right_dx = arrow_sides_length * cos(self.angle - 2.4455)
        right_dy = arrow_sides_length * sin(self.angle - 2.4455)
        right_end = (end_x + right_dx, end_y + right_dy)

        pygame.draw.line(surface, "#FFFFFF", (end_x, end_y), left_end, line_width)
        pygame.draw.line(surface, "#FFFFFF", (end_x, end_y), right_end, line_width)

        return (end_x - self.position.x, end_y - self.position.y)

    def draw(self, surface):
        pygame.draw.circle(surface, self.shape.color, self.position, self.shape.radius)

    def add_angle(self, value: int): self.angle += value
    def set_angle(self, value: int): self.angle = value
    def sub_angle(self, value: int): self.angle -= value
    def get_angle(self): return self.angle

    def set_position(self, position): self.position = position
    def get_position(self): return self.position