import pygame as pg


class ColorUtils:
    @classmethod
    def hex_to_rgb(self, hex_color: pg.Color | pg.typing.ColorLike):
        color_parts = [hex_color[i : i + 2] for i in range(0, len(hex_color), 2)]
        return tuple([int(part, 16) for part in color_parts])

    @classmethod
    def rgb_to_rgba(self, color: pg.Color | pg.typing.ColorLike):
        if len(color) == 3: return tuple(list(color) + [255])
        elif len(color) == 4: return tuple(color)
        else: raise TypeError(f"{color} is not a color")

    @classmethod
    def index_color(self, color: pg.Color | pg.typing.ColorLike):
        hex_chars = set("0123456789ABCDEF")
        if all(symbol in hex_chars for symbol in color):
            return ColorUtils.rgb_to_rgba(ColorUtils.hex_to_rgb(color))
        elif isinstance(color, (tuple, list)):
            if len(color) == 3: return ColorUtils.rgb_to_rgba(color)
            elif len(color) == 4: return color
            else: raise TypeError(f"{color} is not a color")
        else: raise TypeError(f"{color} is not a color")