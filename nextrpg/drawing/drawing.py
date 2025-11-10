from dataclasses import dataclass, replace
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self, override

from frozendict import frozendict
from pygame import BLEND_RGBA_MULT, SRCALPHA, Surface
from pygame.image import load, save
from pygame.transform import flip, gaussian_blur, smoothscale

from nextrpg.config.config import config
from nextrpg.core.cached_decorator import cached
from nextrpg.core.log import Log
from nextrpg.core.metadata import HasMetadata
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.color import TRANSPARENT, WHITE, Alpha, Color
from nextrpg.drawing.relative_animation_like import RelativeAnimationLike
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import ORIGIN, Coordinate
from nextrpg.geometry.dimension import (
    HeightScaling,
    Pixel,
    Size,
    WidthAndHeightScaling,
    WidthScaling,
)
from nextrpg.geometry.padding import Padding
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen

if TYPE_CHECKING:
    from nextrpg.drawing.drawing_on_screen import DrawingOnScreen

log = Log()


@cached(
    lambda: config().resource.drawing_cache_size,
    lambda resource, *args, **kwargs: (
        None if isinstance(resource, Surface) else resource
    ),
)
@dataclass(frozen=True)
class Drawing(AnimationLike, HasMetadata):
    resource: Path | Surface
    color_key: Color | Coordinate | None = None
    convert_alpha: bool | None = None
    allow_background_in_debug: bool = True
    metadata: frozendict[str, Any] = frozendict()

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
        return replace(self, surface=surface)

    def crop(self, area: RectangleAreaOnScreen) -> Self:
        surface = self.pygame.subsurface(area.pygame)
        return replace(self, resource=surface).add_metadata(crop_area=area)

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
    ) -> tuple[DrawingOnScreen, ...]:
        drawing_on_screen = self.drawing_on_screen(coordinate, anchor)
        return (drawing_on_screen,)

    def __mul__(
        self, scaling: WidthScaling | HeightScaling | WidthAndHeightScaling
    ) -> Self:
        size = self.size * scaling
        surface = smoothscale(self.surface, size)
        return replace(self, resource=surface)

    @cached_property
    def visible_rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        rectangle = self.surface.get_bounding_rect()
        coordinate = Coordinate(rectangle.x, rectangle.y)
        size = Size(rectangle.width, rectangle.height)
        return coordinate.as_top_left_of(size).rectangle_area_on_screen

    @cached_property
    def rectangle(self) -> RectangleAreaOnScreen:
        return ORIGIN.as_top_left_of(self.size).rectangle_area_on_screen

    @cached_property
    def surface(self) -> Surface:
        if isinstance(self.resource, Surface):
            return self.resource

        log.debug(t"Loading {self.resource}")
        res = load(self.resource)
        if not self.color_key:
            if self.convert_alpha is None or self.convert_alpha:
                return res.convert_alpha()
            return res.convert()

        if isinstance(self.color_key, Coordinate):
            color = res.get_at(self.color_key)
            res.set_colorkey(color)
        else:
            res.set_colorkey(self.color_key)

        if self.convert_alpha is None or not self.convert_alpha:
            return res.convert()
        return res.convert_alpha()

    def blur(self, radius: int) -> Self:
        surface = gaussian_blur(self.surface, radius)
        return replace(self, resource=surface).add_metadata(blur_radius=radius)

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
    ) -> RelativeAnimationLike:
        from nextrpg.drawing.rectangle_drawing import RectangleDrawing

        rect = RectangleDrawing(
            self.size + padding,
            color,
            width,
            border_radius,
            self.allow_background_in_debug,
        )
        return rect.drawing.shift(-padding.top_left_shift)

    def to_file(self, file: Path) -> None:
        save(self.surface, file)

    @property
    def _debug_surface(self) -> Surface | None:
        if (
            not (debug := config().debug)
            or not (color := debug.drawing_background_color)
            or not self.allow_background_in_debug
        ):
            return None

        size = (self.surface.width, self.surface.height)
        surface = Surface(size, SRCALPHA)
        surface.fill(color)
        surface.blit(self.surface, ORIGIN)
        return surface


def scale_surface(surface: Surface, scaling: float) -> Surface:
    return smoothscale(
        surface, (surface.width * scaling, surface.height * scaling)
    )
