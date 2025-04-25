from core import typing

from .grid_body import GridBody

import random

import pygame

import pymunk


class Grid(pygame.sprite.Group):
    def __init__(self,
                 rect: typing.Union[typing.RectLike, pygame.Rect],
                 count: pygame.typing.Point,
                 grid_body_image: pygame.Surface):
        """
        Creates grid made from pymunk bodies

        :param rect: Defines grid rect
        :param count: Defines the number of bodies in length and width
        :param grid_body_image: Defines image for every grid_body
        """
        super().__init__()

        self.rect = pygame.Rect(rect)

        self.count = count

        self.grid_body_image = grid_body_image
        self.grid_body_colorization_func = self.grid_body_colorize

        self.rebuild()

    def add(self, *spaces_or_sprites: typing.Sequence[typing.Union[pymunk.Space, pygame.sprite.Sprite]]):
        spaces, sprites = [], []

        for obj in spaces_or_sprites:
            if isinstance(obj, pymunk.Space):
                spaces.append(obj)
            elif isinstance(obj, pygame.sprite.Sprite):
                sprites.append(obj)

        for space in spaces:
            for grid_sprite in self.sprites():
                grid_sprite.add(space)

        super().add(*sprites)

    def add_internal(self, space_or_sprite: typing.Union[pymunk.Space, pygame.sprite.Sprite], layer: typing.Literal[None] = None):
        if isinstance(space_or_sprite, pymunk.Space):
            for grid_sprite in self.sprites():
                grid_sprite.add_internal(space_or_sprite)

        if isinstance(space_or_sprite, pygame.sprite.Sprite):
            super().add_internal(space_or_sprite)

    @classmethod
    def draw_preview(self,
                     surface: pygame.Surface,
                     color: typing.ColorLike,
                     rect: typing.Union[typing.RectLike, pygame.Rect],
                     count: typing.Point):
        """
        Draws preview grid without space bodies

        :param count: Defines the number of bodies in length and width
        :param surface: Defines a surface where the grid will be drawed
        """

        rect = pygame.Rect(rect)

        body_width = rect.width / count[0]
        body_height = rect.height / count[1]

        offset_x = rect.centerx - (count[0] - 1) * body_width / 2
        offset_y = rect.centery - (count[1] - 1) * body_height / 2

        for x in range(count[0]):
            for y in range(count[1]):
                pygame.draw.rect(surface, color, ((offset_x + x * body_width - body_width / 2,
                                                offset_y + y * body_height - body_height / 2),
                                                (body_width, body_height)), 1)

    @classmethod
    def get_valid_sizes(self, size: pygame.typing.Point, start: int, stop: int):
        dividebles = [i for i in range(start, stop) if (size[0] * 10) % i == 0 and (size[1] // 2 * 10) % i == 0]
        return [min(dividebles), dividebles[len(dividebles) // 2], max(dividebles)]

    @classmethod
    def grid_body_colorize(self, surface: pygame.Surface):
        surface.fill((random.randint(25, 255),
                      random.randint(25, 255),
                      random.randint(25, 255),
                      255), special_flags = pygame.BLEND_RGB_MULT)

    def kill_all(self):
        for sprite in self.sprites():
            self.kill_sprite(sprite)

    def kill_sprite(self, sprite: pygame.sprite.Sprite):
        for iter_sprite in self.sprites():
            if iter_sprite == sprite:
                self.remove(sprite)
                sprite.kill()

    def rebuild(self):
        body_width = self.rect.width / self.count[0]
        body_height = self.rect.height / self.count[1]

        offset_x = self.rect.center[0] - (self.count[0] - 1) * body_width / 2
        offset_y = self.rect.center[1] - (self.count[1] - 1) * body_height / 2

        for x in range(self.count[0]):
            for y in range(self.count[1]):
                grid_body_surface = pygame.Surface((body_width, body_height), pygame.SRCALPHA)
                grid_body_surface.fill((0, 0, 0, 0))

                grid_body_surface.blit(pygame.transform.smoothscale(self.grid_body_image, (body_width, body_height)))

                self.grid_body_colorization_func(grid_body_surface)

                grid_body_rect = pygame.Rect(0, 0, body_width, body_height)
                grid_body_rect.center = (offset_x + x * body_width,
                                        offset_y + y * body_height)

                grid_body = GridBody(grid_body_rect, grid_body_surface)
                grid_body.add(self)

    def remove(self, *spaces_or_sprites: typing.Sequence[typing.Union[pymunk.Space, pygame.sprite.Sprite]]):
        spaces, sprites = [], []

        for obj in spaces_or_sprites:
            if isinstance(obj, pymunk.Space):
                spaces.append(obj)
            elif isinstance(obj, pygame.sprite.Sprite):
                sprites.append(obj)

        for space in spaces:
            for grid_sprite in self.sprites():
                grid_sprite.add(space)

        super().remove(*sprites)

    def remove_internal(self, space_or_sprite: typing.Union[pymunk.Space, pygame.sprite.Sprite]):
        if isinstance(space_or_sprite, pymunk.Space):
            for grid_sprite in self.sprites():
                grid_sprite.remove_internal(space_or_sprite)

        if isinstance(space_or_sprite, pygame.sprite.Sprite) and space_or_sprite in self.sprites():
            super().remove_internal(space_or_sprite)