from typing import TYPE_CHECKING, Self

from nextrpg.core.time import Millisecond
from nextrpg.drawing.anchor import Anchor
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import ZERO_SIZE, Size
from nextrpg.geometry.sizable import Sizable

if TYPE_CHECKING:
    from nextrpg.animation.animation_like_on_screen import AnimationLikeOnScreen
    from nextrpg.drawing.drawing import Drawing
    from nextrpg.drawing.drawing_group import DrawingGroup
    from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
    from nextrpg.drawing.relative_drawing import RelativeDrawing


class AnimationLike(Sizable):
    drawing: Drawing | DrawingGroup

    @property
    def drawings(self) -> tuple[Drawing, ...]:
        return self.drawing.drawings

    @property
    def no_shift(self) -> RelativeDrawing:
        return self.shift(ZERO_SIZE)

    def shift(
        self, shift: Size, anchor: Anchor = Anchor.TOP_LEFT
    ) -> RelativeDrawing:
        from nextrpg.drawing.relative_drawing import RelativeDrawing

        return RelativeDrawing(self.drawing, shift, anchor)

    def animation_on_screen(
        self, coordinate: Coordinate
    ) -> AnimationLikeOnScreen:
        from nextrpg.animation.animation_like_on_screen import (
            AnimationLikeOnScreen,
        )

        return AnimationLikeOnScreen(coordinate, self)

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

    @property
    def is_complete(self) -> bool:
        return True

    @property
    def top_left(self) -> Coordinate:
        return self.drawing.top_left

    @property
    def size(self) -> Size:
        return self.drawing.size
