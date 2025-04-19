import pygame
from pygame import Rect

import pymunk


class Player(pymunk.Body):
    max_health = 3
    current_health = max_health
    current_speed = 500

    def __init__(self, rect: Rect):
        super().__init__(body_type = pymunk.Body.KINEMATIC)

        self.rect = rect
        self.set_position(self.rect.center)
        self.calculate_colors()

        self.shape = pymunk.Poly.create_box(self, self.rect.size)
        self.shape.elasticity = 1.005

    def calculate_colors(self):
        self.colors = [(0, 0, 0, 255)] + [
            (int(255 * (heart / self.max_health)), int(255 * (1 - heart / self.max_health)), 0, 255)
            for heart in range(self.max_health, 0, -1)
        ]

    def draw(self, surface):
        "Draws player, updates player rect"
        self.rect.center = self.position
        self.shape.color = self.colors[self.current_health]
        pygame.draw.rect(surface, self.shape.color, self.rect)

    def add_health(self, value: int): self.current_health += value
    def set_health(self, value: int): self.current_health = value
    def sub_health(self, value: int): self.current_health -= value
    def get_health(self): return self.current_health

    def add_speed(self, value: int): self.current_speed += value
    def set_speed(self, value: int): self.current_speed = value
    def sub_speed(self, value: int): self.current_speed -= value
    def get_speed(self): return self.current_speed

    def set_position(self, position: pygame.typing.Point):
        self.position = position
        self.rect.center = self.position

    def reset(self, position: pygame.typing.Point):
        self.set_position(position)
        self.set_health(self.max_health)