from core import typing

from pygame import Rect
from pygame.sprite import Group
from pygame.sprite import Sprite

import pymunk
from pymunk import Space


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

    def add(self, *spaces_or_groups: typing.Sequence[typing.Union[Space, Group]]):
        remain_groups = []
        for space_or_group in spaces_or_groups:
            if isinstance(space_or_group, Space):
                space_or_group.add(self.body, *self.segments)
            elif isinstance(space_or_group, Group):
                remain_groups.append(space_or_group)
        super().add(*remain_groups)

    def remove(self, *spaces_or_groups: typing.Sequence[typing.Union[Space, Group]]):
        remain_groups = []
        for space_or_group in spaces_or_groups:
            if isinstance(space_or_group, Space):
                if self.body in space_or_group.bodies:
                    space_or_group.remove(self.body, *self.segments)
            elif isinstance(space_or_group, Group):
                remain_groups.append(space_or_group)
        super().remove(*remain_groups)

    def add_internal(self, space_or_group: typing.Union[Space, Group]):
        if isinstance(space_or_group, Space):
            space_or_group.add(self.body, *self.segments)
        if isinstance(space_or_group, Group):
            super().add_internal(space_or_group)

    def remove_internal(self, space_or_group: typing.Union[Space, Group]):
        if isinstance(space_or_group, Space):
            if self.body in space_or_group.bodies:
                space_or_group.remove(self.body, *self.segments)
        if isinstance(space_or_group, Group):
            super().remove_internal(space_or_group)

    def kill(self):
        if hasattr(self.body, "space") and isinstance(self.body.space, Space):
            self.body.space.remove(self.body, *self.segments)
        super().kill()