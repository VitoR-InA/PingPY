import pygame as pg

import pymunk as pm


class HollowBox:
    def __init__(self,
                 rect: pg.Rect,
                 width: int,
                 space: pm.Space):
        self.shapes = []
        points = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft, rect.topleft]
        for i in range(len(points) - 1):
            segment = pm.Segment(space.static_body, points[i], points[i + 1], width)
            segment.elasticity = 1
            segment.friction = 0
            self.shapes.append(segment)
            space.add(segment)
            
    def get_shapes(self):
        return self.shapes