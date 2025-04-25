from .ball import Ball
from core import typing

from math import sin, cos, radians

import pygame
from pygame import Surface


class BallController:
    def __init__(self, ball: Ball):
        self.ball = ball
        self.ball_angle = -90
        self.ball_angle_rotate_speed = 45

    def get_arrow_points(self):
        size_factor = self.ball.shape.area / 400

        arrow_length = round(50 * size_factor)
        arrow_sides_length = round(25 * size_factor)

        end_x = self.ball.get_position("centerx") + arrow_length * cos(radians(self.ball_angle))
        end_y = self.ball.get_position("centery") + arrow_length * sin(radians(self.ball_angle))

        left_dx = arrow_sides_length * cos(radians(self.ball_angle + 140))
        left_dy = arrow_sides_length * sin(radians(self.ball_angle + 140))

        right_dx = arrow_sides_length * cos(radians(self.ball_angle - 140))
        right_dy = arrow_sides_length * sin(radians(self.ball_angle - 140))

        return {"start_point": (self.ball.get_position()),
                "end_point": (end_x, end_y),
                "left_end_point": (end_x + left_dx, end_y + left_dy),
                "right_end_point": (end_x + right_dx, end_y + right_dy)}

    def draw_arrow(self, surface: Surface):
        size_factor = self.ball.shape.area / 400

        arrow_points = self.get_arrow_points()
        arrow_line_width = round(3 * size_factor)

        pygame.draw.line(surface, (255, 255, 255, 255), arrow_points["end_point"], arrow_points["left_end_point"], arrow_line_width)
        pygame.draw.line(surface, (255, 255, 255, 255), arrow_points["end_point"], arrow_points["right_end_point"], arrow_line_width)

    def get_angle(self): return self.ball_angle
    def set_angle(self, new_angle: int): self.ball_angle = new_angle

    def rotate_left(self, time_delta: typing.Optional[float] = 1):
        self.ball_angle -= self.ball_angle_rotate_speed * time_delta

    def rotate_right(self, time_delta: typing.Optional[float] = 1):
        self.ball_angle += self.ball_angle_rotate_speed * time_delta

    def update_rotate_speed(self, new_speed: float):
        self.ball_angle_rotate_speed = new_speed

    def launch(self, impulse: float):
        self.ball.body.velocity = [(end_point - ball_point) * impulse for ball_point, end_point in zip(self.ball.get_position(), self.get_arrow_points()["end_point"])]