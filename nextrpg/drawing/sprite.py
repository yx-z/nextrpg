from collections.abc import Iterable
from functools import cached_property
from typing import TYPE_CHECKING, Protocol, Self, runtime_checkable

from pygame import Surface

from nextrpg.core.time import Millisecond
from nextrpg.drawing.color import Alpha
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import ORIGIN, Coordinate
from nextrpg.geometry.directional_offset import Degree, DirectionalOffset
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.geometry.scaling import (
    HeightScaling,
    WidthAndHeightScaling,
    WidthScaling,
)
from nextrpg.geometry.sizable import Sizable
from nextrpg.geometry.size import Height, Size, Width

if TYPE_CHECKING:
    from nextrpg.animation.animation_on_screen import AnimationOnScreen
    from nextrpg.drawing.drawing import Drawing
    from nextrpg.drawing.drawing_group import DrawingGroup
    from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
    from nextrpg.drawing.shifted_sprite import ShiftedSprite

type BlurRadius = int


@runtime_checkable
class Sprite(Sizable, Protocol):
    @property
    def drawing(self) -> Drawing | DrawingGroup: ...

    @cached_property
    def pygame(self) -> Surface:
        return self.drawing.pygame

    @cached_property
    def top_left(self) -> Coordinate:
        return ORIGIN

    def __mul__(
        self, scaling: WidthScaling | HeightScaling | WidthAndHeightScaling
    ) -> Drawing | DrawingGroup:
        return self.drawing * scaling

    @cached_property
    def size(self) -> Size:
        return self.drawing.size

    @cached_property
    def drawings(self) -> tuple[Drawing, ...]:
        return self.drawing.drawings

    def __add__(
        self, shift: Coordinate | Width | Height | Size | DirectionalOffset
    ) -> ShiftedSprite:
        return self.shift(shift.size)

    def __sub__(
        self, shift: Coordinate | Width | Height | Size | DirectionalOffset
    ) -> ShiftedSprite:
        return self + -shift

    def shift(
        self,
        shift: Coordinate | Width | Height | Size | DirectionalOffset,
        anchor: Anchor = Anchor.TOP_LEFT,
    ) -> ShiftedSprite:
        from nextrpg.drawing.shifted_sprite import (
            ShiftedSprite,
        )

        return ShiftedSprite(self, shift, anchor)

    def animation_on_screen(
        self, coordinate: Coordinate, anchor: Anchor = Anchor.TOP_LEFT
    ) -> AnimationOnScreen:
        from nextrpg.animation.animation_on_screen import (
            AnimationOnScreen,
        )

        return AnimationOnScreen(coordinate, self, anchor)

    def drawing_on_screen(
        self, coordinate: Coordinate, anchor: Anchor = Anchor.TOP_LEFT
    ) -> DrawingOnScreen:
        from nextrpg.drawing.drawing_on_screens import DrawingOnScreens

        drawing_on_screens = self.drawing_on_screens(coordinate, anchor)
        return DrawingOnScreens(drawing_on_screens).drawing_on_screen

    def drawing_on_screens(
        self, coordinate: Coordinate, anchor: Anchor = Anchor.TOP_LEFT
    ) -> tuple[DrawingOnScreen, ...]:
        return self.drawing.drawing_on_screens(coordinate, anchor)

    def tick(self, time_delta: Millisecond) -> Self:
        return self

    def flip(
        self, horizontal: bool = False, vertical: bool = False
    ) -> Drawing | DrawingGroup:
        return self.drawing.flip(horizontal, vertical)

    @cached_property
    def is_complete(self) -> bool:
        return True

    def alpha(self, alpha: Alpha) -> Drawing | DrawingGroup:
        return self.drawing.alpha(alpha)

    def cut(self, area: RectangleAreaOnScreen) -> Drawing | DrawingGroup:
        return self.drawing.cut(area)

    def crop(self, area: RectangleAreaOnScreen) -> Drawing | DrawingGroup:
        return self.drawing.crop(area)

    def blur(self, radius: BlurRadius) -> Drawing:
        return self.drawing.blur(radius)

    def rotate(self, degree: Degree) -> Drawing | DrawingGroup:
        return self.drawing.rotate(degree)


def tick_optional[T](resource: T | None, time_delta: Millisecond) -> T | None:
    if resource:
        return resource.tick(time_delta)
    return None


def tick_all[T](
    resource: Iterable[T], time_delta: Millisecond
) -> tuple[T, ...]:
    return tuple(t.tick(time_delta) for t in resource)
