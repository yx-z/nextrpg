from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from functools import cached_property
from typing import override

from pygame import Surface

from nextrpg.core.color import TRANSPARENT, Color
from nextrpg.core.dimension import Size
from nextrpg.draw.drawing import Drawing


@dataclass(frozen=True)
class TransparentDrawing(Drawing):
    _: KW_ONLY
    color: Color

    @property
    def fully_transparent(self) -> bool:
        return self.color == TRANSPARENT

    @override
    @property
    def surface(self) -> Surface:
        if self.fully_transparent:
            return Surface((0, 0))
        return super().surface

    @override
    @cached_property
    def size(self) -> Size:
        if self.fully_transparent:
            return Drawing(self.resource).size
        return super().size
