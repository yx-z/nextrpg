import logging
import os
from dataclasses import replace
from functools import cached_property
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self, override

from pygame import BLEND_RGBA_MULT, SRCALPHA, Surface, image
from pygame.transform import flip, gaussian_blur, rotate, smoothscale

from nextrpg.core.cached_decorator import cached
from nextrpg.core.dataclass_with_default import dataclass_with_default, default
from nextrpg.core.logger import Logger
from nextrpg.core.metadata import METADATA_CACHE_KEY, HasMetadata, Metadata
from nextrpg.core.save import LoadFromSave
from nextrpg.drawing.color import TRANSPARENT, WHITE, Alpha, Color
from nextrpg.drawing.shifted_sprite import ShiftedSprite
from nextrpg.drawing.sprite import BlurRadius, Sprite
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import ORIGIN, Coordinate
from nextrpg.geometry.dimension import (
    Pixel,
)
from nextrpg.geometry.directional_offset import Degree
from nextrpg.geometry.padding import Padding
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.geometry.scaling import (
    HeightScaling,
    WidthAndHeightScaling,
    WidthScaling,
)
from nextrpg.geometry.size import ZERO_SIZE, Size

if TYPE_CHECKING:
    from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
    from nextrpg.drawing.drawing_on_screens import DrawingOnScreens

on_screen_logger = Logger("drawing")
console_logger = logging.getLogger("drawing")


def _metadata_key(cls: type, *args: Any, **kwargs: Any) -> Metadata | None:
    if (metadata := kwargs.get("metadata")) and metadata[
        0
    ] == METADATA_CACHE_KEY:
        return metadata
    return None


def _default_metadata(self: Drawing) -> Metadata:
    if isinstance(self.resource, Surface):
        return ()
    return METADATA_CACHE_KEY, ("resource", str(self.resource))


@cached(
    lambda resource_config: resource_config.drawing_cache_size,
    _metadata_key,
)
@dataclass_with_default(frozen=True)
class Drawing(Sprite, HasMetadata, LoadFromSave):
    resource: str | Path | Surface
    allow_background_in_debug: bool = True
    metadata: Metadata = default(_default_metadata)

    @override
    def save_data_this_class(self) -> str | bytes:
        if isinstance(self.resource, Surface):
            io = BytesIO()
            image.save(self.surface, io)
            return io.getvalue()
        return os.fspath(self.resource)

    @override
    @classmethod
    def load_this_class_from_save(cls, data: str | bytes) -> Self:
        if isinstance(data, bytes):
            io = BytesIO(data)
            surface = image.load(io).convert_alpha()
            return cls(surface)
        path = Path(data)
        return cls(path)

    @override
    @cached_property
    def drawing(self) -> Drawing:
        return self

    @override
    @cached_property
    def drawings(self) -> tuple[Drawing, ...]:
        return (self,)

    @override
    def __str__(self) -> str:
        if isinstance(self.resource, Surface):
            resource = ""
        else:
            resource = f", {self.resource}"

        if self.metadata:
            metadata = f", metadata={self.metadata}"
        else:
            metadata = ""

        return f"Drawing({self.size}{resource}{metadata})"

    @override
    def __repr__(self) -> str:
        return str(self)

    @override
    @cached_property
    def size(self) -> Size:
        return Size(self.surface.width, self.surface.height)

    @property
    def pygame(self) -> Surface:
        if self._debug_surface:
            return self._debug_surface
        return self.surface

    def with_border_radius(self, border_radius: Pixel) -> Self:
        rectangle = self.rectangle_area_on_screen.fill(
            WHITE, border_radius=border_radius, allow_background_in_debug=False
        )
        surface = self.surface.copy()
        surface.blit(
            rectangle.drawing.surface, ORIGIN, special_flags=BLEND_RGBA_MULT
        )
        return replace(self, resource=surface)

    def crop(self, area: RectangleAreaOnScreen) -> Self:
        surface = self.pygame.subsurface(area.pygame)
        return replace(self, resource=surface).add_metadata(crop=area)

    def trim(self, trim: Padding) -> Self:
        if trim == Padding():
            return self
        area = trim.top_left.as_top_left_of(
            self.size - trim
        ).rectangle_area_on_screen
        return self.crop(area).add_metadata(trim=trim)

    @override
    def alpha(self, alpha: Alpha) -> Self:
        surface = self.surface.copy()
        surface.set_alpha(alpha)
        return replace(self, resource=surface).add_metadata(alpha=alpha)

    @override
    def drawing_on_screen(
        self, coordinate: Coordinate, anchor: Anchor = Anchor.TOP_LEFT
    ) -> DrawingOnScreen:
        from nextrpg.drawing.drawing_on_screen import DrawingOnScreen

        return DrawingOnScreen(coordinate, self, anchor)

    @override
    def drawing_on_screens(
        self, coordinate: Coordinate, anchor: Anchor = Anchor.TOP_LEFT
    ) -> DrawingOnScreens:
        return self.drawing_on_screen(coordinate, anchor).drawing_on_screens

    def __mul__(
        self, scaling: WidthScaling | HeightScaling | WidthAndHeightScaling
    ) -> Self:
        size = self.size * scaling
        surface = smoothscale(self.surface, size)
        return replace(self, resource=surface)

    @cached_property
    def rectangle(self) -> RectangleAreaOnScreen:
        return ORIGIN.as_top_left_of(self.size).rectangle_area_on_screen

    @cached_property
    def surface(self) -> Surface:
        if isinstance(self.resource, Surface):
            return self.resource

        on_screen_logger.debug(f"Loading {Path(self.resource).name}")
        console_logger.debug(f"Loading {self.resource}")
        return image.load(self.resource).convert_alpha()

    @override
    def blur(self, radius: BlurRadius) -> Self:
        surface = gaussian_blur(self.surface, radius)
        return replace(self, resource=surface).add_metadata(blur_radius=radius)

    @override
    def rotate(self, degree: Degree) -> Self:
        surface = rotate(self.surface, degree)
        return replace(self, resource=surface).add_metadata(
            rotate_degree=degree
        )

    @override
    def cut(self, area: RectangleAreaOnScreen) -> Self:
        surface = self.surface.copy()
        surface.fill(TRANSPARENT, (area.top_left, area.size))
        return replace(self, resource=surface).add_metadata(cut_area=area)

    @override
    def flip(self, horizontal: bool = False, vertical: bool = False) -> Self:
        surface = flip(self.surface, horizontal, vertical)
        return replace(self, resource=surface).add_metadata(
            flip_x=horizontal, flip_y=vertical
        )

    def background(
        self,
        color: Color,
        padding: Padding = Padding(),
        border_radius: Pixel = -1,
        width: Pixel = 0,
    ) -> ShiftedSprite:
        from nextrpg.drawing.rectangle_drawing import RectangleDrawing

        rect = RectangleDrawing(
            self.size + padding,
            color,
            width,
            border_radius,
            self.allow_background_in_debug,
        )
        return rect.drawing - padding.top_left

    def to_file(self, file: str | Path) -> None:
        image.save(self.surface, file)

    @property
    def _debug_surface(self) -> Surface | None:
        from nextrpg.config.config import config

        if (
            not (debug := config().debug)
            or not (color := debug.drawing_background)
            or not self.allow_background_in_debug
        ):
            return None

        size = (self.surface.width, self.surface.height)
        surface = Surface(size, SRCALPHA).convert_alpha()
        surface.fill(color.pygame)
        surface.blit(self.surface, ORIGIN)
        return surface


EMPTY_DRAWING = Drawing(Surface(ZERO_SIZE, SRCALPHA))
