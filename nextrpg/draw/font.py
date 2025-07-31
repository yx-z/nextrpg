from dataclasses import dataclass
from functools import cached_property

import pygame
from pygame.font import SysFont

from nextrpg.core.dimension import Pixel, Size


@dataclass(frozen=True)
class Font:
    size: int
    name: str | None = None
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    script: str | None = None

    @cached_property
    def pygame(self) -> pygame.Font:
        font = SysFont(self.name, self.size, self.bold, self.italic)
        if self.underline:
            font.set_underline(True)
        if self.strikethrough:
            font.set_strikethrough(True)
        if self.script:
            font.set_script(self.script)
        return font

    def text_size(self, text: str) -> Size:
        width, height = self.pygame.size(text)
        return Size(width, height)

    @property
    def text_height(self) -> Pixel:
        return self.pygame.get_linesize()
