from dataclasses import dataclass
from functools import cached_property
from typing import Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.core.color import TRANSPARENT
from nextrpg.core.dimension import Size
from nextrpg.core.direction import Direction
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.polygon import PolygonDrawing, RectangleDrawing


@dataclass(frozen=True)
class PolygonCharacterDrawing(CharacterDrawing):
    arg: Size | RectangleDrawing | PolygonDrawing

    @override
    @cached_property
    def drawing(self) -> Drawing:
        if isinstance(self.arg, Size):
            return RectangleDrawing(self.arg, TRANSPARENT)
        return self.arg

    @override
    def turn(self, direction: Direction) -> Self:
        return self

    @override
    def tick_move(self, time_delta: Millisecond) -> Self:
        return self

    @override
    def tick_idle(self, time_delta: Millisecond) -> Self:
        return self
