from dataclasses import dataclass
from functools import cached_property
from typing import Any, Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.polygon_drawing import PolygonDrawing
from nextrpg.drawing.rectangle_drawing import RectangleDrawing


@dataclass(frozen=True, kw_only=True)
class PolygonCharacterDrawing(CharacterDrawing):
    rect_or_poly: RectangleDrawing | PolygonDrawing

    @override
    @cached_property
    def save_data_this_class(self) -> dict[str, Any]:
        is_rect = isinstance(self.rect_or_poly, RectangleDrawing)
        return {
            "is_rect": is_rect,
            "rect_or_poly": self.rect_or_poly.save_data,
        }

    @override
    def update_this_class_from_save(self, data: dict[str, Any]) -> Self:
        if data["is_rect"]:
            drawing_class = RectangleDrawing
        else:
            drawing_class = PolygonDrawing
        rect_or_poly = drawing_class.load_from_save(data["rect_or_poly"])
        return PolygonCharacterDrawing(rect_or_poly=rect_or_poly)

    @override
    @cached_property
    def drawing(self) -> Drawing:
        return self.rect_or_poly.drawing
