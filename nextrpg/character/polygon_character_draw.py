from dataclasses import dataclass
from functools import cached_property
from typing import Self, override

from nextrpg.character.character_draw import CharacterDraw
from nextrpg.core.color import TRANSPARENT
from nextrpg.core.dimension import Size
from nextrpg.core.direction import Direction
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import Draw, PolygonDraw, RectangleDraw


@dataclass(frozen=True)
class PolygonCharacterDraw(CharacterDraw):
    arg: Size | RectangleDraw | PolygonDraw

    @override
    @cached_property
    def draw(self) -> Draw:
        if isinstance(self.arg, Size):
            return RectangleDraw(self.arg, TRANSPARENT)
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
