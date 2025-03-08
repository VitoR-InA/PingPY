from game_modules.constants import *

import pygame
from pygame import Rect

import pymunk


class Player(pymunk.Body):
    max_health = PLAYER_DEFAULT_HEALTH
    speed = PLAYER_DEFAULT_SPEED

    def __init__(self, rect: Rect):
        self.rect = rect # Player rect

        self.health = self.max_health # Player health

        self.colors = [(0, 0, 0, 255)] + [
            (int(255 * (heart / self.max_health)), int(255 * (1 - heart / self.max_health)), 0, 255)
            for heart in range(self.health, 0, -1)
        ]

        # Player body
        super().__init__(body_type = pymunk.Body.KINEMATIC)
        self.position = self.rect.topleft

        # Player shape
        self.shape = pymunk.Poly.create_box(self, self.rect.size)
        self.shape.elasticity = 1.005
        self.shape.friction = 0

    def draw(self, surface):
        "Draws player, updates player rect"
        self.rect.center = self.position
        self.shape.color = self.colors[self.health]
        pygame.draw.rect(surface, self.shape.color, self.rect)

    def set_position(self, position: pygame.typing.Point): self.position = position

    def set_size(self, size: pygame.typing.Point):
        self.rect.size = size
        self.shape.area = size

    def take_damage(self, damage: int): self.health -= damage