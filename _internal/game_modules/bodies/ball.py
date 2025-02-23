from math import cos, sin, radians

import pygame

import pymunk


class Ball:
    def __init__(self,
                 color: pygame.Color,
                 center: pygame.typing.Point,
                 radius: float,
                 space: pymunk.Space):
        #Ball angle
        self.angle = 90

        #Ball body
        self.moment = pymunk.moment_for_circle(10, radius, 0)
        self.body = pymunk.Body(10, self.moment)
        self.body.position = center

        #Ball shape
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.collision_type = 1
        self.shape.elasticity = 1.005
        self.shape.friction = 0
        self.shape.color = color

        space.add(self.body, self.shape)

    def draw_arrow(self, surface: pygame.Surface):
        "Draws arrow at given coordinates, defines ball direction"
        size_factor = self.shape.radius / 10

        arrow_length = round(50 * size_factor)
        end_x = self.body.position[0] + arrow_length * cos(radians(self.angle))
        end_y = self.body.position[1] - arrow_length * sin(radians(self.angle))

        arrow_sides_length = round(25 * size_factor)
        left_end_x = end_x + arrow_sides_length * cos(radians(self.angle + 140))
        left_end_y = end_y - arrow_sides_length * sin(radians(self.angle + 140))
        right_end_x = end_x + arrow_sides_length * cos(radians(self.angle - 140))
        right_end_y = end_y - arrow_sides_length * sin(radians(self.angle - 140))

        pygame.draw.line(surface, "#FFFFFF", (end_x, end_y), (left_end_x, left_end_y), round(3 * size_factor))
        pygame.draw.line(surface, "#FFFFFF", (end_x, end_y), (right_end_x, right_end_y), round(3 * size_factor))

        return (end_x - self.body.position[0], end_y - self.body.position[1])

    def set_angle(self, value: int = 90):
        self.angle = value

    def set_position(self, position):
        self.body.position = position
        
    def draw(self, surface):
        pygame.draw.circle(surface, self.shape.color, self.body.position, self.shape.radius)