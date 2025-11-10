from dataclasses import dataclass
from functools import cached_property
from typing import override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.polygon_drawing import PolygonDrawing
from nextrpg.drawing.rectangle_drawing import RectangleDrawing


@dataclass(frozen=True, kw_only=True)
class PolygonCharacterDrawing(CharacterDrawing):
    rect_or_poly: RectangleDrawing | PolygonDrawing

    @override
    @cached_property
    def drawing(self) -> Drawing:
        return self.rect_or_poly.drawing
