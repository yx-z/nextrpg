from dataclasses import dataclass
from functools import cached_property

import pygame
from pygame.font import SysFont

from nextrpg.core.dimension import Pixel, Size


@dataclass(frozen=True)
class Font:
    size: int
    name: str | None = None

    @cached_property
    def pygame(self) -> pygame.Font:
        return SysFont(self.name, self.size)

    def text_size(self, text: str) -> Size:
        width, height = self.pygame.size(text)
        return Size(width, height)

    @property
    def text_height(self) -> Pixel:
        return self.pygame.get_linesize()
