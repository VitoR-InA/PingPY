import collections
import collections.abc

import numbers

import pygame
from pygame.typing import *

import pymunk

from typing import *


BodyTypes: TypeAlias = Literal["DYNAMIC", "KINEMATIC", "STATIC"]

class _HasGroupAttributes(Protocol):
    def draw(self) -> None: ...

GroupLike = Union[pygame.sprite.AbstractGroup, pygame.sprite.Group, _HasGroupAttributes]

RectPoint: TypeAlias = Literal["topleft", "top", "topright", "x", "y",
                               "left", "center", "centerx", "centery", "right",
                               "midleft", "midtop", "midbottom", "midright",
                               "bottomleft", "bottom", "bottomright"]

class _HasSpriteAttributes(Protocol):
    @property
    def image(self) -> Union["pygame.Surface", Callable[[], "pygame.Surface"]]: ...
    @property
    def rect(self) -> Union["RectLike", Callable[[], "RectLike"]]: ...

SpriteLike = Union[pygame.sprite.Sprite, Hashable, _HasSpriteAttributes]

# cleanup namespace
del pygame, pymunk
