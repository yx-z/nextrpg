import os
from dataclasses import dataclass, replace
from functools import cached_property
from pathlib import Path
from typing import Self

import pygame
from pygame.font import SysFont

from nextrpg.geometry.dimension import Pixel
from nextrpg.geometry.size import Size


@dataclass(frozen=True)
class FontSize:
    value: Pixel


@dataclass(frozen=True)
class Font:
    font_size: FontSize
    name: str | Path | None = None
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    script: str | None = None

    @cached_property
    def bolded(self) -> Self:
        return replace(self, bold=True)

    @cached_property
    def italicized(self) -> Self:
        return replace(self, italic=True)

    @cached_property
    def underlined(self) -> Self:
        return replace(self, underline=True)

    @cached_property
    def strikethroughed(self) -> Self:
        return replace(self, strikethrough=True)

    def with_script(self, script: str) -> Self:
        return replace(self, script=script)

    def with_font_size(self, font_size: FontSize) -> Self:
        return replace(self, font_size=font_size)

    @cached_property
    def pygame(self) -> pygame.Font:
        if isinstance(self.name, Path) or os.path.exists(self.name):
            font = pygame.Font(self.name)
            font.set_bold(self.bold)
            font.set_italic(self.italic)
        else:
            size_px = int(self.font_size.value)
            font = SysFont(self.name, size_px, self.bold, self.italic)
        font.set_underline(self.underline)
        font.set_strikethrough(self.strikethrough)
        if self.script:
            font.set_script(self.script)
        return font

    def text_size(self, text: str) -> Size:
        width, height = self.pygame.size(text)
        return Size(width, height)
