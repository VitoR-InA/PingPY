from game_modules.constants import *

import pygame
from pygame import Rect

import pymunk


class Player(pymunk.Body):
    max_health = PLAYER_DEFAULT_HEALTH
    speed = PLAYER_DEFAULT_SPEED

    def __init__(self, rect: pygame.typing.RectLike):
        # Player rect
        self.rect = rect

        # Player health
        self.health = self.max_health

        self.colors = []
        for heart in range(1, self.health + 1):
            factor = heart / self.max_health
            self.colors.append((int(255 * factor), int(255 * (1 - factor)), 0, 255))
        self.colors.append((7, 7, 7, 255))
        self.colors.reverse()

        # Player body
        super().__init__(body_type = pymunk.Body.KINEMATIC)
        self.position = self.rect.topleft

        # Player shape
        self.shape = pymunk.Poly.create_box(self, self.rect.size)
        self.shape.elasticity = 1.005
        self.shape.friction = 0

    def draw(self, surface):
        # Draws player
        self.rect.center = self.position
        self.shape.color = self.colors[self.health]
        pygame.draw.rect(surface, self.shape.color, self.rect)

    def set_position(self, position):
        self.position = position

    def take_damage(self, damage: int):
        self.health -= damage