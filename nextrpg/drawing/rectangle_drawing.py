from dataclasses import dataclass
from functools import cached_property
from typing import Any, Self, override

from pygame import SRCALPHA, Rect, Surface
from pygame.draw import rect

from nextrpg.core.metadata import METADATA_CACHE_KEY
from nextrpg.core.save import LoadFromSave
from nextrpg.drawing.color import Color
from nextrpg.drawing.drawing import Drawing
from nextrpg.geometry.coordinate import ORIGIN
from nextrpg.geometry.dimension import Pixel
from nextrpg.geometry.size import Size


@dataclass(frozen=True)
class RectangleDrawing(LoadFromSave):
    size: Size
    color: Color
    width: Pixel = 0
    border_radius: Pixel = -1
    allow_background_in_debug: bool = True

    @override
    @cached_property
    def save_data_this_class(self) -> dict[str, Any]:
        return {
            "size": self.size.save_data,
            "color": self.color.save_data,
            "width": self.width,
            "border_radius": self.border_radius,
            "allow_background_in_debug": self.allow_background_in_debug,
        }

    @override
    @classmethod
    def load_this_class_from_save(cls, data: dict[str, Any]) -> Self:
        size = Size.load_from_save(data["size"])
        color = Color.load_from_save(data["color"])
        width = data["width"]
        border_radius = data["border_radius"]
        allow_background_in_debug = data["allow_background_in_debug"]
        return cls(size, color, width, border_radius, allow_background_in_debug)

    @cached_property
    def drawing(self) -> Drawing:
        surface = Surface(self.size, SRCALPHA).convert_alpha()
        rectangle = Rect(ORIGIN, self.size)
        rect(
            surface,
            self.color.pygame,
            rectangle,
            self.width,
            self.border_radius,
        )
        metadata = (
            METADATA_CACHE_KEY,
            ("size", self.size),
            ("color", self.color),
            ("width", self.width),
            ("border_radius", self.border_radius),
        )
        return Drawing(surface, self.allow_background_in_debug, metadata)
