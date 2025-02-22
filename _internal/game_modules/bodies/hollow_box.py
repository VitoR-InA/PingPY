import pygame
from pygame import Rect

import pymunk


class HollowBox:
    def __init__(self,
                 rect: Rect,
                 width: int,
                 space: pymunk.Space):
        self.shapes = []
        points = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft, rect.topleft]
        for i in range(len(points) - 1):
            segment = pymunk.Segment(space.static_body, points[i], points[i + 1], width)
            segment.elasticity = 1.005
            segment.friction = 0
            self.shapes.append(segment)
            space.add(segment)
            
    def get_shapes(self):
        return self.shapes