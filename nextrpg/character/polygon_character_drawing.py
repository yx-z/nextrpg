from dataclasses import KW_ONLY, dataclass
from functools import cached_property
from typing import Any, Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.core.dataclass_with_default import private_init_below
from nextrpg.core.save import LoadFromSave
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.polygon_drawing import PolygonDrawing
from nextrpg.drawing.rectangle_drawing import RectangleDrawing


def _update_polygon_character_drawing(
    character_drawing: CharacterDrawing, data: dict[str, Any]
) -> PolygonCharacterDrawing:
    return PolygonCharacterDrawing.load_from_save(data)


@dataclass(frozen=True, kw_only=True)
class PolygonCharacterDrawing(CharacterDrawing, LoadFromSave):
    rect_or_poly: RectangleDrawing | PolygonDrawing
    _: KW_ONLY = private_init_below()
    update_function = _update_polygon_character_drawing

    @override
    @cached_property
    def save_data(self) -> dict[str, Any]:
        return super().save_data | {
            "is_rect": isinstance(self, RectangleDrawing),
            "rect_or_poly": self.rect_or_poly.save_data,
        }

    @override
    @classmethod
    def load_from_save(cls, data: dict[str, Any]) -> Self:
        if data["is_rect"]:
            drawing_class = RectangleDrawing
        else:
            drawing_class = PolygonDrawing
        rect_or_poly = drawing_class.load_from_save(data["rect_or_poly"])
        return cls(rect_or_poly=rect_or_poly)

    @override
    @cached_property
    def drawing(self) -> Drawing:
        return self.rect_or_poly.drawing
