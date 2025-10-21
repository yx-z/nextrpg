from functools import cached_property
from typing import TYPE_CHECKING, Self

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
    from nextrpg.drawing.relative_animation_like import RelativeAnimationLike


class AnimationLike(Sizable):
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
    ) -> RelativeAnimationLike:
        from nextrpg.drawing.relative_animation_like import (
            RelativeAnimationLike,
        )

        return RelativeAnimationLike(self, shift, anchor)

    def animation_on_screen(self, coordinate: Coordinate) -> AnimationOnScreen:
        from nextrpg.animation.animation_on_screen import (
            AnimationOnScreen,
        )

        return AnimationOnScreen(coordinate, self)

    def drawing_on_screen(self, coordinate: Coordinate) -> DrawingOnScreen:
        from nextrpg.drawing.drawing_on_screens import DrawingOnScreens

        drawing_on_screens = self.drawing_on_screens(coordinate)
        return DrawingOnScreens(drawing_on_screens).drawing_on_screen

    def drawing_on_screens(
        self, coordinate: Coordinate
    ) -> tuple[DrawingOnScreen, ...]:
        return self.drawing.drawing_on_screens(coordinate)

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
