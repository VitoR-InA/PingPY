from core import typing

from multipledispatch import dispatch

import pygame

import pymunk


class Entity(pygame.sprite.Sprite):
    """
    Basic entity class. The entity is always a box.
    
    :param rect: 
    """
    def __init__(self,
                 rect: typing.Union[typing.RectLike, pygame.Rect],
                 mass: float = 0,
                 moment: float = 0,
                 elasticity: float = 0,
                 density: float = 0,
                 friction: float = 0,
                 collision_type: typing.Optional[int] = None, 
                 body_type: int = pymunk.Body.DYNAMIC):
        super().__init__()

        self.rect = pygame.Rect(rect)

        if not moment: moment = pymunk.moment_for_box(mass, rect.size)
        self.body = pymunk.Body(mass = mass, moment = moment, body_type = body_type)
        self.body.position = self.rect.center

        self.shape = pymunk.Poly.create_box(body = self.body, size = self.rect.size)
        if elasticity: self.shape.elasticity = elasticity
        if density: self.shape.density = density
        if friction: self.shape.friction = friction

        if collision_type is not None:
            self.shape.collision_type = collision_type

        self.rebuild_rect()

    def add(self, *spaces_or_groups: typing.collections.abc.Sequence[typing.Union[pymunk.Space, typing.GroupLike]]):
        spaces, groups = [], []

        for obj in spaces_or_groups:
            if isinstance(obj, pymunk.Space):
                spaces.append(obj)
            elif isinstance(obj, pygame.sprite.AbstractGroup):
                groups.append(obj)

        for space in spaces:
            self.add_internal(space)

        super().add(*groups)

    def add_internal(self, space_or_group: typing.Union[pymunk.Space, typing.GroupLike]):
        if isinstance(space_or_group, pymunk.Space):
            space_or_group.add(self.body, self.shape)

        if isinstance(space_or_group, pygame.sprite.Group):
            super().add_internal(space_or_group)

    @dispatch(pygame.Rect)
    def clamp_ip(self, rect: pygame.Rect):
        self.rect.clamp_ip(rect)
        self.body.position = self.center

    @dispatch(typing.collections.abc.Sequence, typing.collections.abc.Sequence)
    def clamp_ip(self, left_top: typing.Point, width_height: typing.Point):
        self.clamp_ip(pygame.Rect(left_top, width_height))

    @dispatch(typing.numbers.Real, typing.numbers.Real, typing.numbers.Real, typing.numbers.Real)
    def clamp_ip(self, left: float, top: float, width: float, height: float):
        self.clamp_ip(pygame.Rect(left, top, width, height))

    @dispatch(pygame.Rect)
    def clip(self, rect: pygame.Rect):
        return self.rect.clip(rect)

    @dispatch(typing.collections.abc.Sequence, typing.collections.abc.Sequence)
    def clip(self, left_top: typing.Point, width_height: typing.Point):
        return self.clip(pygame.Rect(left_top, width_height))

    @dispatch(typing.numbers.Real, typing.numbers.Real, typing.numbers.Real, typing.numbers.Real)
    def clip(self, left: float, top: float, width: float, height: float):
        return self.clip(pygame.Rect(left, top, width, height))

    @dispatch(pygame.Rect)
    def clipline(self, rect: pygame.Rect):
        return self.rect.clipline(rect)

    @dispatch(typing.collections.abc.Sequence, typing.collections.abc.Sequence)
    def clipline(self, first_point: typing.Point, second_point: typing.Point):
        return self.clipline(pygame.Rect(first_point, second_point))

    @dispatch(typing.numbers.Real, typing.numbers.Real, typing.numbers.Real, typing.numbers.Real)
    def clipline(self, x1: float, y1: float, x2: float, y2: float):
        return self.clipline(pygame.Rect(x1, y1, x2, y2))

    @dispatch(typing.numbers.Real, typing.numbers.Real)
    def collidepoint(self, x: float, y: float):
        return self.rect.collidepoint(x, y)

    @dispatch(typing.collections.abc.Sequence)
    def collidepoint(self, x_y: typing.Point):
        return self.collidepoint(*x_y)

    @dispatch(pygame.Rect)
    def colliderect(self, rect: pygame.Rect):
        return self.rect.colliderect(rect)

    @dispatch(typing.collections.abc.Sequence, typing.collections.abc.Sequence)
    def colliderect(self, left_top: typing.Point, width_height: typing.Point):
        self.colliderect(pygame.Rect(left_top, width_height))

    @dispatch(typing.numbers.Real, typing.numbers.Real, typing.numbers.Real, typing.numbers.Real)
    def colliderect(self, left: float, top: float, width: float, height: float):
        self.colliderect(pygame.Rect(left, top, width, height))

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
        return self.collidedictall(rect_dict, values)

    @dispatch(pygame.Rect)
    def fit(self, rect: typing.RectLike):
        return self.rect.fit(rect)

    @dispatch(typing.collections.abc.Sequence, typing.collections.abc.Sequence)
    def fit(self, left_top: typing.Point, width_height: typing.Point):
        return self.fit(pygame.Rect(left_top, width_height))

    @dispatch(typing.numbers.Real, typing.numbers.Real, typing.numbers.Real, typing.numbers.Real)
    def fit(self, left: float, top: float, width: float, height: float):
        return self.fit(pygame.Rect(left, top, width, height))

    def get_position(self, point: typing.Optional[typing.RectPoint] = None):
        if point and hasattr(self.rect, point) and point in typing.get_args(typing.RectPoint):
            return getattr(self.rect, point)
        else: return self.rect.center

    @dispatch(typing.numbers.Real, typing.numbers.Real)
    def inflate_ip(self, x: float, y: float):
        def increase_with_sign(num, increase_by):
            return num + (num / abs(num)) * increase_by\
                if num != 0 else 0

        original_vertices = self.shape.get_vertices()
        new_vertices = [(increase_with_sign(z, x // 2), increase_with_sign(w, y // 2))
                        for (z, w) in original_vertices]

        self.shape.unsafe_set_vertices(new_vertices)
        if self.body.space is not None:
            self.body.space.reindex_shapes_for_body(self.body)

        self.rebuild_rect()

    @dispatch(typing.collections.abc.Sequence)
    def inflate_ip(self, inflate_by: typing.Point):
        self.inflate_ip(*inflate_by)

    def kill(self):
        if self.body.space is not None:
            self.body.space.remove(self.body)

        if self.shape.space is not None:
            self.shape.space.remove(self.shape)

        super().kill()

    @dispatch(typing.numbers.Real, typing.numbers.Real)
    def move(self, x: float, y: float):
        self.rect.move(x, y)

    @dispatch(typing.collections.abc.Sequence)
    def move(self, move_by: typing.Point):
        self.move(*move_by)

    @dispatch(typing.numbers.Real, typing.numbers.Real)
    def move_ip(self, x: float, y: float):
        self.rect.move_ip(x, y)
        self.body.position = self.rect.center

    @dispatch(typing.collections.abc.Sequence)
    def move_ip(self, move_by: typing.Point):
        self.move_ip(*move_by)

    def move_to(self, **kwargs: typing.Dict[typing.RectPoint, typing.Point]):
        self.rect.move_to(**kwargs)

    def move_to_ip(self, **kwargs: typing.Dict[typing.RectPoint, typing.Point]):
        for key, value in kwargs.items():
            if key in typing.get_args(typing.RectPoint)\
                and hasattr(self.rect, key):
                    setattr(self.rect, key, value)
        self.body.position = self.rect.center

    def rebuild_rect(self):
        bounding_box = self.shape.cache_bb()
        self.rect.update(pygame.Rect(bounding_box.left, bounding_box.top,
                                     bounding_box.right - bounding_box.left,
                                     bounding_box.bottom - bounding_box.top))
        self.rect.normalize()

    def remove(self, *spaces_or_groups: typing.collections.abc.Sequence[typing.Union[pymunk.Space, typing.GroupLike]]):
        spaces, groups = [], []

        for obj in spaces_or_groups:
            if isinstance(obj, pymunk.Space):
                spaces.append(obj)
            elif isinstance(obj, pygame.sprite.AbstractGroup):
                groups.append(obj)

        for space in spaces:
            self.remove_internal(space)

        super().remove(*groups)

    def remove_internal(self, space_or_group: typing.Union[pymunk.Space, typing.GroupLike]):
        if isinstance(space_or_group, pymunk.Space):
            if self.body in space_or_group.bodies:
                space_or_group.remove(self.body)
            if self.shape in space_or_group.shapes:
                space_or_group.remove(self.shape)

        if isinstance(space_or_group, pygame.sprite.AbstractGroup) and space_or_group in self.groups():
                super().remove_internal(space_or_group)

    @dispatch(typing.numbers.Real, typing.numbers.Real)
    def scale_by_ip(self, x: float, y: float):
        scale_factor = [self.rect.size[0] * x - self.rect.size[0],
                        self.rect.size[1] * y - self.rect.size[1]]
        self.inflate_ip(scale_factor)

    @dispatch(typing.collections.abc.Sequence)
    def scale_by_ip(self, scale_by: typing.Point):
        self.scale_by_ip(*scale_by)

    @dispatch(pygame.Rect)
    def union_ip(self, rect: pygame.Rect):
        raise NotImplementedError("Pymunk doesn't support union_ip yet")

    @dispatch(typing.collections.abc.Sequence, typing.collections.abc.Sequence)
    def union_ip(self, left_top: typing.Point, width_height: typing.Point):
        self.union_ip(pygame.Rect(left_top, width_height))

    @dispatch(typing.numbers.Real, typing.numbers.Real, typing.numbers.Real, typing.numbers.Real)
    def union_ip(self, left: float, top: float, width: float, height: float):
        self.union_ip(pygame.Rect(left, top, width, height))

    @dispatch(typing.collections.abc.Sequence)
    def unionall_ip(self, rects: typing.SequenceLike):
        raise NotImplementedError("Pymunk doesn't support unionall_ip yet")

    def update(self): self.rect.center = self.body.position