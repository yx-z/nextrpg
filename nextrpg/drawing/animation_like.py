from typing import TYPE_CHECKING, Self

from nextrpg.core.time import Millisecond
from nextrpg.drawing.anchor import Anchor
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import ZERO_SIZE, Size
from nextrpg.geometry.sizable import Sizable

if TYPE_CHECKING:
    from nextrpg.animation.animation_on_screen import AnimationOnScreen
    from nextrpg.drawing.drawing import Drawing
    from nextrpg.drawing.drawing_group import DrawingGroup
    from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
    from nextrpg.drawing.relative_drawing import RelativeDrawing


class AnimationLike(Sizable):
    @property
    def drawing(self) -> Drawing | DrawingGroup: ...

    @property
    def top_left(self) -> Coordinate:
        return Coordinate(0, 0)

    @property
    def size(self) -> Size:
        return self.drawing.size

    @property
    def drawings(self) -> tuple[Drawing, ...]:
        return self.drawing.drawings

    @property
    def with_no_shift(self) -> RelativeDrawing:
        return self.shift(ZERO_SIZE)

    def shift(
        self, shift: Size, anchor: Anchor = Anchor.TOP_LEFT
    ) -> RelativeDrawing:
        from nextrpg.drawing.relative_drawing import RelativeDrawing

        return RelativeDrawing(self.drawing, shift, anchor)

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

    @property
    def is_complete(self) -> bool:
        return True
