import pygame
from pygame import Rect

import pymunk


class Player(pymunk.Body):
    def __init__(self,
                 rect: Rect,
                 health: int):
        # Player rect
        self.rect = rect

        # Player health
        self.health = health

        self.colors = []
        for heart in range(1, self.health + 1):
            factor = heart / health
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
        # Draw player
        self.rect.center = self.position
        self.shape.color = self.colors[self.health]
        pygame.draw.rect(surface, self.shape.color, Rect((self.position[0] - self.rect.size[0] / 2, self.position[1] - self.rect.size[1] / 2), self.rect.size))

    def set_position(self, position):
        self.position = position

    def take_damage(self, damage: int):
        self.health -= damage