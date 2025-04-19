from .grid_body import GridBody

from itertools import product

import random

import pygame
from pygame import Rect
from pygame import Surface
from pygame.sprite import Sprite
from pygame.sprite import LayeredUpdates

from pymunk import Space

import typing


class Grid(LayeredUpdates):
    def __init__(self, rect: Rect, count: pygame.typing.Point, grid_body_image: Surface):
        """
        Creates grid made from pymunk bodies

        :param rect: Defines grid rect
        :param count: Defines the number of bodies in length and width
        :param grid_body_image: Defines image for every grid_body
        """
        super().__init__()

        self.rect = rect

        self.count = count

        self.grid_body_image = grid_body_image
        self.grid_body_colorization_func = self.grid_body_colorize

        self.rebuild()

    @classmethod
    def draw_preview(self,
                     surface: pygame.Surface,
                     color: pygame.typing.ColorLike,
                     rect: pygame.typing.RectLike,
                     count: pygame.typing.Point):
        """
        Draws preview grid without space bodies

        :param count: Defines the number of bodies in length and width
        :param surface: Defines a surface where the grid will be drawed
        """
        body_width = rect.width / count[0]
        body_height = rect.height / count[1]

        offset_x = rect.centerx - (count[0] - 1) * body_width / 2
        offset_y = rect.centery - (count[1] - 1) * body_height / 2

        for x, y in product(range(count[0]), range(count[1])):
            pygame.draw.rect(surface, color, ((offset_x + x * body_width - body_width / 2,
                                               offset_y + y * body_height - body_height / 2),
                                              (body_width, body_height)), 1)

    @classmethod
    def get_valid_sizes(self, size: pygame.typing.Point, start: int, stop: int):
        dividebles = [i for i in range(start, stop) if (size[0] * 10) % i == 0 and (size[1] // 2 * 10) % i == 0]
        return [min(dividebles), dividebles[len(dividebles) // 2], max(dividebles)]

    @classmethod
    def grid_body_colorize(self, surface: Surface):
        surface.fill((random.randint(25, 255), random.randint(25, 255), random.randint(25, 255), 255),
                     special_flags = pygame.BLEND_RGB_MULT)

    def rebuild(self):
        body_width = self.rect.width / self.count[0]
        body_height = self.rect.height / self.count[1]

        offset_x = self.rect.center[0] - (self.count[0] - 1) * body_width / 2
        offset_y = self.rect.center[1] - (self.count[1] - 1) * body_height / 2

        for x, y in product(range(self.count[0]), range(self.count[1])):
            grid_body_surface = Surface((body_width, body_height), pygame.SRCALPHA)
            grid_body_surface.fill((0, 0, 0, 0))

            grid_body_surface.blit(pygame.transform.smoothscale(self.grid_body_image, (body_width, body_height)))

            self.grid_body_colorization_func(grid_body_surface)

            grid_body_rect = Rect(0, 0, body_width, body_height)
            grid_body_rect.center = (offset_x + x * body_width,
                                     offset_y + y * body_height)

            grid_body = GridBody(grid_body_rect, grid_body_surface)
            self.add(grid_body)

    def add(self, *spaces_or_sprites: typing.Sequence[typing.Union[Space, Sprite]]):
        remain_sprites = []
        for space_or_sprite in spaces_or_sprites:
            if isinstance(space_or_sprite, Space):
                for grid_sprite in self.sprites():
                    grid_sprite.add(space_or_sprite)
            elif isinstance(space_or_sprite, Sprite):
                remain_sprites.append(space_or_sprite)
        super().add(*remain_sprites)

    def remove(self, *spaces_or_sprites: typing.Sequence[typing.Union[Space, Sprite]]):
        remain_sprites = []
        for space_or_sprite in spaces_or_sprites:
            if isinstance(space_or_sprite, Space):
                for grid_sprite in self.sprites():
                    grid_sprite.remove(space_or_sprite)
            elif isinstance(space_or_sprite, Sprite):
                remain_sprites.append(space_or_sprite)
        super().remove(*remain_sprites)

    def add_internal(self, space_or_sprite: typing.Union[Space, Sprite], layer: None = None):
        if isinstance(space_or_sprite, Space):
            for grid_sprite in self.sprites():
                grid_sprite.add_internal(space_or_sprite)
        if isinstance(space_or_sprite, Sprite):
            super().add_internal(space_or_sprite)

    def remove_internal(self, space_or_sprite: typing.Union[Space, Sprite]):
        if isinstance(space_or_sprite, Space):
            for grid_sprite in self.sprites():
                grid_sprite.remove_internal(space_or_sprite)
        if isinstance(space_or_sprite, Sprite):
            super().remove_internal(space_or_sprite)

    def kill(self):
        for sprite in self.sprites(): sprite.kill()