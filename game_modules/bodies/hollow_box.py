from pygame import Rect

import pymunk

class HollowBox(pymunk.Body):
    def __init__(self,
                 rect: Rect,
                 width: int):
        super().__init__(body_type = pymunk.Body.STATIC)
        self.position = rect.center

        self.segments = [
            pymunk.Segment(self, (-rect.width/2, -rect.height/2), (-rect.width/2, rect.height/2), width),
            pymunk.Segment(self, (rect.width/2, -rect.height/2), (rect.width/2, rect.height/2), width),
            pymunk.Segment(self, (-rect.width/2, rect.height/2), (rect.width/2, rect.height/2), width),
            pymunk.Segment(self, (-rect.width/2, -rect.height/2), (rect.width/2, -rect.height/2), width)
        ]

        for segment in self.segments:
            segment.elasticity = 1.005