from dataclasses import dataclass
from functools import cached_property
from typing import Any, Self, override

from nextrpg import to_module_and_attribute
from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.core.save import LoadFromSave
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.polygon_drawing import PolygonDrawing
from nextrpg.drawing.rectangle_drawing import RectangleDrawing


@dataclass(frozen=True, kw_only=True)
class PolygonCharacterDrawing(CharacterDrawing, LoadFromSave):
    rect_or_poly: RectangleDrawing | PolygonDrawing

    @override
    @cached_property
    def save_data(self) -> dict[str, Any]:
        return super().save_data | {
            "is_rect": isinstance(self, RectangleDrawing),
            "rect_or_poly": self.rect_or_poly.save_data,
            "update": to_module_and_attribute(
                _update_polygon_character_drawing
            ),
        }

    @override
    @classmethod
    def load_from_save(cls, data: dict[str, Any]) -> Self:
        if data["is_rect"]:
            rect_or_poly = RectangleDrawing.load_from_save(data["rect_or_poly"])
        else:
            rect_or_poly = PolygonDrawing.load_from_save(data["rect_or_poly"])
        return cls(rect_or_poly=rect_or_poly)

    @override
    @cached_property
    def drawing(self) -> Drawing:
        return self.rect_or_poly.drawing


def _update_polygon_character_drawing(
    character_drawing: CharacterDrawing, data: dict[str, Any]
) -> PolygonCharacterDrawing:
    return PolygonCharacterDrawing.load_from_save(data)
