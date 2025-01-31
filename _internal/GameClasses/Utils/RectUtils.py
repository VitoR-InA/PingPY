import pygame as pg


class RectUtils:
    @classmethod
    def index_rect(self, rect: pg.Rect | pg.typing.RectLike):
        if isinstance(rect, pg.Rect): return rect
        elif isinstance(rect, (tuple, list)): return pg.Rect(*rect)
        else: raise TypeError(f"{rect} is not a rect")