from dataclasses import KW_ONLY, dataclass
from functools import cached_property
from typing import Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.polygon_drawing import PolygonDrawing
from nextrpg.drawing.rectangle_drawing import RectangleDrawing
from nextrpg.geometry.direction import Direction


@dataclass(frozen=True)
class PolygonCharacterDrawing(CharacterDrawing):
    _: KW_ONLY
    rect_or_poly: RectangleDrawing | PolygonDrawing
    direction: Direction = Direction.DOWN

    @override
    @cached_property
    def drawing(self) -> Drawing:
        return self.rect_or_poly.drawing

    @override
    def turn(self, direction: Direction) -> Self:
        return self

    @override
    def tick_move(self, time_delta: Millisecond) -> Self:
        return self
