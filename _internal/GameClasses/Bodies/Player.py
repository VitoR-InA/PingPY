from _internal.GameClasses.Utils.RectUtils import RectUtils

import pygame as pg

import pymunk as pm


class Player:
    def __init__(self,
                 rect: pg.Rect,
                 health: int,
                 speed: int,
                 space: pm.Space):
        #Player rect
        self.rect = RectUtils.index_rect(rect)

        #Player health
        self.health = health
        self.colors = []
        for heart in range(1, self.health + 1):
            factor = heart / health
            self.colors.append((int(255 * factor), int(255 * (1 - factor)), 0, 255))
        self.colors.append((7, 7, 7, 255))
        self.colors.reverse()

        #Player speed
        self.speed = speed
        
        #Player body
        self.body = pm.Body(body_type=pm.Body.KINEMATIC)
        self.body.position = self.rect.topleft
        
        #Player shape
        self.shape = pm.Poly.create_box(self.body, self.rect.size)
        self.shape.elasticity = 1
        self.shape.friction = 0
        
        #Add player to space
        space.add(self.body, self.shape)

    def draw(self, surface):
        #Change color
        self.shape.color = self.colors[self.health]

        #Draw player
        pg.draw.rect(surface, self.shape.color, pg.Rect((self.body.position[0] - self.rect.size[0] / 2, self.body.position[1] - self.rect.size[1] / 2), self.rect.size))

    def set_position(self, position):
        self.body.position = position

    def take_damage(self, damage: int = 1):
        self.health -= damage

    def update(self, time_delta: float):
        keys = pg.key.get_pressed()
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            self.body.velocity = ()