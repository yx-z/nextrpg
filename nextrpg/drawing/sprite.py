from functools import cached_property
from typing import TYPE_CHECKING, Protocol, Self, runtime_checkable

from nextrpg.core.time import Millisecond
from nextrpg.drawing.color import Alpha
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import ORIGIN, Coordinate
from nextrpg.geometry.dimension import (
    HeightScaling,
    Size,
    WidthAndHeightScaling,
    WidthScaling,
)
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.geometry.sizable import Sizable

if TYPE_CHECKING:
    from nextrpg.animation.animation_on_screen import AnimationOnScreen
    from nextrpg.drawing.drawing import Drawing
    from nextrpg.drawing.drawing_group import DrawingGroup
    from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
    from nextrpg.drawing.shifted_sprite import ShiftedSprite


@runtime_checkable
class Sprite(Sizable, Protocol):
    @property
    def drawing(self) -> Drawing | DrawingGroup: ...

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

    def shift(
        self, shift: Size, anchor: Anchor = Anchor.TOP_LEFT
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
