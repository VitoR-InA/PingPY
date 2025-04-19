from multipledispatch import dispatch

from pygame import Rect
from pygame import Surface
from pygame.sprite import Group
from pygame.sprite import Sprite

import pymunk
import pymunk.util
from pymunk import Space

from core import typing


class GridBody(Sprite):
    def __init__(self, rect: Rect, image: Surface):
        super().__init__() # Sprite init

        self.rect = rect # Sprite rect !Not for use!

        self.original_image = image

        self.body = pymunk.Body(body_type = pymunk.Body.STATIC)
        self.body.position = self.rect.center

        self.shape = pymunk.Poly.create_box(body = self.body, size = self.rect.size)
        self.shape.elasticity = 1.005
        self.shape.collision_type = 2

    @dispatch(typing.numbers.Real, typing.numbers.Real)
    def move_ip(self, x: float, y: float):
        position = self.body.position
        self.body.position = [position[0] + x,
                              position[1] + y]
        self.rect.move_ip(x, y)

    @dispatch(typing.collections.abc.Sequence)
    def move_ip(self, move_by: typing.Point):
        self.move_ip(*move_by)

    def move_to_ip(self, **kwargs):
        for key, value in kwargs:
            if hasattr(self.rect, key): setattr(self.rect, key, value)
        self.body.position = self.rect.center

    @dispatch(typing.numbers.Real, typing.numbers.Real)
    def inflate_ip(self, x: float, y: float):
        def increase_with_sign(num, increase_by):
            if num == 0: return 0
            return num + (num / abs(num)) * increase_by

        original_vertices = self.shape.get_vertices()
        new_vertices = [(increase_with_sign(z, x), increase_with_sign(w, y))
                        for (z, w) in original_vertices]
        if len(pymunk.util.convex_hull(new_vertices)) != len(new_vertices): raise ValueError

        self.shape.unsafe_set_vertices(new_vertices)
        if self.body.space is not None:
            self.body.space.reindex_shapes_for_body(self.body)

        self.rect.inflate_ip(x, y)

        self.rebuild()

    @dispatch(typing.collections.abc.Sequence)
    def inflate_ip(self, inflate_by: typing.Point):
        self.inflate_ip(*inflate_by)

    @dispatch(typing.numbers.Real, typing.numbers.Real)
    def scale_by_ip(self, x: float, y: float):
        scale_factor = [self.size[0] * x - self.size[0],
                        self.size[1] * y - self.size[1]]
        self.inflate_ip(scale_factor)

    @dispatch(typing.collections.abc.Sequence)
    def scale_by_ip(self, scale_by: typing.Point):
        self.scale_by_ip(*scale_by)

    @dispatch(Rect)
    def clamp(self, rect: Rect):
        return self.rect.clamp(rect)

    @dispatch(typing.collections.abc.Sequence, typing.collections.abc.Sequence)
    def clamp(self, left_top: typing.Point, width_height: typing.Point):
        return self.clamp(Rect(left_top, width_height))

    @dispatch(typing.numbers.Real, typing.numbers.Real, typing.numbers.Real, typing.numbers.Real)
    def clamp(self, left: float, top: float, width: float, height: float):
        return self.clamp(Rect(left, top, width, height))

    @dispatch(Rect)
    def clamp_ip(self, rect: Rect):
        self.rect.clamp_ip(rect)
        self.body.position = self.rect.center

    @dispatch(typing.collections.abc.Sequence, typing.collections.abc.Sequence)
    def clamp_ip(self, left_top: typing.Point, width_height: typing.Point):
        self.clamp_ip(Rect(left_top, width_height))

    @dispatch(typing.numbers.Real, typing.numbers.Real, typing.numbers.Real, typing.numbers.Real)
    def clamp_ip(self, left: float, top: float, width: float, height: float):
        self.clamp_ip(Rect(left, top, width, height))

    @dispatch(Rect)
    def clip(self, rect: Rect):
        return self.rect.clip(rect)

    @dispatch(typing.collections.abc.Sequence, typing.collections.abc.Sequence)
    def clip(self, left_top: typing.Point, width_height: typing.Point):
        return self.clip(Rect(left_top, width_height))

    @dispatch(typing.numbers.Real, typing.numbers.Real, typing.numbers.Real, typing.numbers.Real)
    def clip(self, left: float, top: float, width: float, height: float):
        return self.clip(Rect(left, top, width, height))

    @dispatch(Rect)
    def clipline(self, rect: Rect):
        return self.rect.clipline(rect)

    @dispatch(typing.collections.abc.Sequence, typing.collections.abc.Sequence)
    def clipline(self, first_point: typing.Point, second_point: typing.Point):
        return self.clipline(Rect(first_point, second_point))

    @dispatch(typing.numbers.Real, typing.numbers.Real, typing.numbers.Real, typing.numbers.Real)
    def clipline(self, x1: float, y1: float, x2: float, y2: float):
        return self.clipline(Rect(x1, y1, x2, y2))

    @dispatch(Rect)
    def union(self, rect: Rect):
        return self.rect.union(rect)

    @dispatch(typing.collections.abc.Sequence, typing.collections.abc.Sequence)
    def union(self, left_top: typing.Point, width_height: typing.Point):
        return self.union(Rect(left_top, width_height))

    @dispatch(typing.numbers.Real, typing.numbers.Real, typing.numbers.Real, typing.numbers.Real)
    def union(self, left: float, top: float, width: float, height: float):
        return self.union(Rect(left, top, width, height))

    @dispatch(Rect)
    def union_ip(self, rect: Rect):
        raise NotImplementedError("Pymunk shape is not compatible with union")

    @dispatch(typing.collections.abc.Sequence, typing.collections.abc.Sequence)
    def union_ip(self, left_top: typing.Point, width_height: typing.Point):
        self.union_ip(Rect(left_top, width_height))

    @dispatch(typing.numbers.Real, typing.numbers.Real, typing.numbers.Real, typing.numbers.Real)
    def union_ip(self, left: float, top: float, width: float, height: float):
        self.union_ip(Rect(left, top, width, height))

    @dispatch(typing.collections.abc.Sequence)
    def unionall_ip(self, rect_sequence: typing.SequenceLike):
        raise NotImplementedError("Pymunk shape is not compatible with unionall")

    @dispatch(Rect)
    def fit(self, rect: typing.RectLike):
        return self.rect.fit(rect)

    @dispatch(typing.collections.abc.Sequence, typing.collections.abc.Sequence)
    def fit(self, left_top: typing.Point, width_height: typing.Point):
        return self.fit(Rect(left_top, width_height))

    @dispatch(typing.numbers.Real, typing.numbers.Real, typing.numbers.Real, typing.numbers.Real)
    def fit(self, left: float, top: float, width: float, height: float):
        return self.fit(Rect(left, top, width, height))

    @dispatch(Rect)
    def contains(self, rect: typing.RectLike):
        return self.rect.contains(rect)

    @dispatch(typing.collections.abc.Sequence, typing.collections.abc.Sequence)
    def contains(self, left_top: typing.Point, width_height: typing.Point):
        return self.contains(Rect(left_top, width_height))

    @dispatch(typing.numbers.Real, typing.numbers.Real, typing.numbers.Real, typing.numbers.Real)
    def contains(self, left: float, top: float, width: float, height: float):
        return self.contains(Rect(left, top, width, height))

    @dispatch(typing.numbers.Real, typing.numbers.Real)
    def collidepoint(self, x: float, y: float):
        return self.rect.collidepoint(x, y)

    @dispatch(typing.collections.abc.Sequence)
    def collidepoint(self, x_y: typing.Point):
        return self.collidepoint(*x_y)

    @dispatch(Rect)
    def colliderect(self, rect: Rect):
        return self.rect.colliderect(rect)

    @dispatch(typing.collections.abc.Sequence, typing.collections.abc.Sequence)
    def colliderect(self, left_top: typing.Point, width_height: typing.Point):
        self.colliderect(Rect(left_top, width_height))

    @dispatch(typing.numbers.Real, typing.numbers.Real, typing.numbers.Real, typing.numbers.Real)
    def colliderect(self, left: float, top: float, width: float, height: float):
        self.colliderect(Rect(left, top, width, height))

    def collidelist(self, rect_list: typing.SequenceLike[typing.RectLike]):
        return self.rect.collidelist(rect_list)
    
    def collidelistall(self, rect_list: typing.SequenceLike[typing.RectLike]):
        return self.rect.collidelistall(rect_list)
    
    def collideobjects(self, objects: typing.SequenceLike[typing.Any], key: typing.Optional[typing.Callable[[typing.Any], typing.RectLike]] = None):
        return self.rect.collideobjects(objects, key)

    def collideobjectsall(self, objects: typing.SequenceLike[typing.Any], key: typing.Optional[typing.Callable[[typing.Any], typing.RectLike]] = None):
        return self.rect.collideobjectsall(objects, key)

    def collidedict(self, rect_dict: typing.Union[typing.Dict[typing.RectLike, typing.Any], typing.Dict[typing.Any, typing.RectLike]], values: typing.Literal[False] = False):
        return self.rect.collidedict(rect_dict, values)

    def collidedictall(self, rect_dict: typing.Union[typing.Dict[typing.RectLike, typing.Any], typing.Dict[typing.Any, typing.RectLike]], values: typing.Literal[False] = False):
        return self.rect.collidedictall(rect_dict, values)

    def rebuild(self): self.image = self.original_image

    def add(self, *spaces_or_groups: typing.Sequence[typing.Union[Space, Group]]):
        remain_groups = []
        for space_or_group in spaces_or_groups:
            if isinstance(space_or_group, Space):
                space_or_group.add(self.body, self.shape)
            elif isinstance(space_or_group, Group):
                remain_groups.append(space_or_group)
        super().add(*remain_groups)

    def remove(self, *spaces_or_groups: typing.Sequence[typing.Union[Space, Group]]):
        remain_groups = []
        for space_or_group in spaces_or_groups:
            if isinstance(space_or_group, Space):
                if self.body in space_or_group.bodies:
                    space_or_group.remove(self.body)
                if self.shape in space_or_group.shapes:
                    space_or_group.remove(self.shape)
            elif isinstance(space_or_group, Group):
                remain_groups.append(space_or_group)
        super().remove(*remain_groups)

    def add_internal(self, space_or_group: typing.Union[Space, Group]):
        if isinstance(space_or_group, Space):
            space_or_group.add(self.body, self.shape)
        if isinstance(space_or_group, Group):
            super().add_internal(space_or_group)

    def remove_internal(self, space_or_group: typing.Union[Space, Group]):
        if isinstance(space_or_group, Space):
            if self.body in space_or_group.bodies:
                space_or_group.remove(self.body)
            if self.shape in space_or_group.shapes:
                space_or_group.remove(self.shape)
        if isinstance(space_or_group, Group):
            super().remove_internal(space_or_group)

    def kill(self):
        if hasattr(self.body, "space") and isinstance(self.body.space, Space):
            self.body.space.remove(self.body)
        if hasattr(self.shape, "space") and isinstance(self.shape.space, Space):
            self.shape.space.remove(self.shape)
        super().kill()

    def update(self, *args, **kwargs):
        self.rect.center = self.body.position
        super().update(*args, **kwargs)