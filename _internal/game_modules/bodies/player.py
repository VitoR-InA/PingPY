import pygame
from pygame import Rect

import pymunk


class Player:
    def __init__(self,
                 rect: Rect,
                 health: int,
                 speed: int,
                 space: pymunk.Space):
        #Player rect
        self.rect = rect

        #Player health
        self.health = health
        self.max_health = health
        self.colors = []
        for heart in range(1, self.health + 1):
            factor = heart / health
            self.colors.append((int(255 * factor), int(255 * (1 - factor)), 0, 255))
        self.colors.append((7, 7, 7, 255))
        self.colors.reverse()

        #Player speed
        self.speed = speed
        
        #Player body
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = self.rect.topleft
        
        #Player shape
        self.shape = pymunk.Poly.create_box(self.body, self.rect.size)
        self.shape.elasticity = 1.005
        self.shape.friction = 0
        
        #Add player to space
        space.add(self.body, self.shape)

    def draw(self, surface):
        #Change color
        self.shape.color = self.colors[self.health]

        #Draw player
        pygame.draw.rect(surface, self.shape.color, Rect((self.body.position[0] - self.rect.size[0] / 2, self.body.position[1] - self.rect.size[1] / 2), self.rect.size))

    def set_position(self, position):
        self.body.position = position

    def take_damage(self, damage: int = 1):
        self.health -= damage