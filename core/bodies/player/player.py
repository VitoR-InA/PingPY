from multipledispatch import dispatch

import pygame
from pygame import Rect
from pygame import Surface
from pygame.sprite import Group
from pygame.sprite import Sprite

import pymunk
import pymunk.util
from pymunk import Space

from core import typing


class Player(Sprite):
    def __init__(self, rect: Rect, image: Surface,
                 health: int, speed: float):
        super().__init__() # Sprite init

        self.rect = rect

        self.original_image = image

        self.current_health = health
        self.max_health = health

        self.current_speed = speed
        self.original_speed = speed

        self.body = pymunk.Body(body_type = pymunk.Body.KINEMATIC)
        self.body.position = self.rect.center

        self.shape = pymunk.Poly.create_box(body = self.body, size = self.rect.size)
        self.shape.elasticity = 1.005

        self.rebuild()

    @dispatch(typing.numbers.Real, typing.numbers.Real)
    def move_ip(self, x: float, y: float):
        position = self.body.position
        self.body.position = [position.x + x,
                              position.y + y]
        self.rect.move_ip(x, y)

    @dispatch(typing.collections.abc.Sequence)
    def move_ip(self, move_by: typing.Point):
        self.move_ip(*move_by)

    def move_to_ip(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.rect, key):
                setattr(self.rect, key, value)
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
    def clamp_ip(self, rect: Rect):
        self.rect.clamp_ip(rect)
        self.body.position = self.center

    @dispatch(typing.collections.abc.Sequence, typing.collections.abc.Sequence)
    def clamp_ip(self, left_top: typing.Point, width_height: typing.Point):
        self.clamp_ip(Rect(left_top, width_height))

    @dispatch(typing.numbers.Real, typing.numbers.Real, typing.numbers.Real, typing.numbers.Real)
    def clamp_ip(self, left: float, top: float, width: float, height: float):
        self.clamp_ip(Rect(left, top, width, height))

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
    def unionall_ip(self, rect_SequenceLike: typing.SequenceLike):
        self.rect.collidelist()
        raise NotImplementedError("Pymunk shape is not compatible with unionall")

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

    def collidedict(self, rect_dict: dict, values: bool = False):
        return self.rect.collidedict(rect_dict, values)

    def collidedictall(self, rect_dict: dict, values: bool = False):
        return self.collidedictall(rect_dict, values)

    def set_image(self, new_image: Surface):
        self.original_image = new_image
        self.rebuild()

    def update_image(self):
        self.image = self.health_surfaces[self.health]

    def get_image(self):
        return self.original_image

    def heal(self, heal_by: int):
        self.health += heal_by
        self.update_image()

    def damage(self, damage_by: int):
        self.health -= damage_by
        self.update_image()

    def set_health(self, new_health: int):
        self.health = new_health
        self.update_image()

    def get_health(self): return self.health

    def set_max_health(self, new_max_health: int,
                       has_to_rebuild: bool = True):
        self.max_health = new_max_health
        if has_to_rebuild: self.rebuild()

    def set_speed(self, new_speed: float):
        self.speed = new_speed

    def get_speed(self):
        return self.speed

    def rebuild(self):
        health_surface = Surface(self.rect.size, pygame.SRCALPHA)
        health_surface.fill((0, 0, 0, 0))

        self.health_surfaces = [health_surface]

        for health in range(self.max_health, 0, -1):
            health_surface = Surface(self.rect.size, pygame.SRCALPHA)
            health_surface.fill((0, 0, 0, 0))

            health_surface.blit(pygame.transform.smoothscale(self.original_image, self.rect.size))

            health_surface.fill((int(255 * (health / self.max_health)),
                                 int(255 * (1 - health / self.max_health)),
                                 0, 255), special_flags = pygame.BLEND_RGB_MULT)

            self.health_surfaces.append(health_surface)

        self.image = self.health_surfaces[self.health]

    def add(self, *spaces_or_groups: typing.typing.collections.abc.Sequence[typing.Union[Space, Group]]):
        remain_groups = []
        for index, space_or_group in enumerate(spaces_or_groups):
            if isinstance(space_or_group, Space):
                space_or_group.add(self.body, self.shape)
            elif isinstance(space_or_group, Group):
                remain_groups.append(space_or_group)
        super().add(*remain_groups)

    def remove(self, *spaces_or_groups: typing.typing.collections.abc.Sequence[typing.Union[Space, Group]]):
        remain_groups = []
        for index, space_or_group in enumerate(spaces_or_groups):
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