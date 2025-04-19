import collections
import collections.abc

import numbers

from pygame.typing import *

from typing import *


NamePoint: TypeAlias = Literal["topleft", "top", "topright", "x", "y",
                               "left", "center", "centerx", "centery", "right",
                               "midleft", "midtop", "midbottom", "midright",
                               "bottomleft", "bottom", "bottomright"]