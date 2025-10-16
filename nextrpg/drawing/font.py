from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self

import pygame
from pygame.font import SysFont

from nextrpg.geometry.dimension import Height, Size


@dataclass(frozen=True)
class Font:
    size: Height
    name: str | None = None
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

    def scripted(self, script: str) -> Self:
        return replace(self, script=script)

    def sized(self, size: Height) -> Self:
        return replace(self, size=size)

    @cached_property
    def pygame(self) -> pygame.Font:
        size = int(self.size.value)
        font = SysFont(self.name, size, self.bold, self.italic)
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

    @cached_property
    def text_height(self) -> Height:
        return Height(self.pygame.get_linesize())
