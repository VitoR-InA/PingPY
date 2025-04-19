from pygame import Rect
from pygame.sprite import Sprite

import pymunk

class HollowBox(Sprite):
    def __init__(self, rect: Rect, width: int):
        super().__init__() # Sprite init

        self.rect = rect

        self.body = pymunk.Body(body_type = pymunk.Body.STATIC)
        self.body.position = self.rect.center

        self.width = width

        self.rebuild()

    def rebuild(self):
        self.segments = [
            pymunk.Segment(self.body, (-self.rect.width / 2, -self.rect.height / 2), (-self.rect.width / 2, self.rect.height / 2), self.width),
            pymunk.Segment(self.body, (self.rect.width / 2, -self.rect.height / 2), (self.rect.width / 2, self.rect.height / 2), self.width),
            pymunk.Segment(self.body, (-self.rect.width / 2, self.rect.height / 2), (self.rect.width / 2, self.rect.height / 2), self.width),
            pymunk.Segment(self.body, (-self.rect.width / 2, -self.rect.height / 2), (self.rect.width / 2, -self.rect.height / 2), self.width)
        ]

        for segment in self.segments:
            segment.elasticity = 1.005