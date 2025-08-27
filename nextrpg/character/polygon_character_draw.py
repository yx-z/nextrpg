from dataclasses import KW_ONLY, dataclass
from typing import Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.core.direction import Direction
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.polygon_drawing import PolygonDrawing
from nextrpg.draw.rectangle_drawing import RectangleDrawing


@dataclass(frozen=True)
class PolygonCharacterDrawing(CharacterDrawing):
    _: KW_ONLY
    rect_or_poly: RectangleDrawing | PolygonDrawing
    direction: Direction = Direction.DOWN

    @override
    @property
    def drawing(self) -> Drawing:
        return self.rect_or_poly.drawing

    @override
    def turn(self, direction: Direction) -> Self:
        return self

    @override
    def tick_move(self, time_delta: Millisecond) -> Self:
        return self

    @override
    def tick_idle(self, time_delta: Millisecond) -> Self:
        return self
