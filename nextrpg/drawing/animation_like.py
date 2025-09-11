from typing import TYPE_CHECKING, Self

from nextrpg.core.time import Millisecond
from nextrpg.drawing.anchor import Anchor
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.sizable import Sizable

if TYPE_CHECKING:
    from nextrpg.drawing.drawing import Drawing
    from nextrpg.drawing.drawing_group import DrawingGroup
    from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
    from nextrpg.drawing.relative_drawing import RelativeDrawing


class AnimationLike(Sizable):
    drawing: Drawing | DrawingGroup

    def shift(
        self, shift: Size, anchor: Anchor = Anchor.TOP_LEFT
    ) -> RelativeDrawing:
        from nextrpg.drawing.relative_drawing import RelativeDrawing

        return RelativeDrawing(self.drawing, shift, anchor)

    def drawing_on_screens(
        self, coordinate: Coordinate
    ) -> tuple[DrawingOnScreen, ...]:
        return self.drawing.drawing_on_screens(coordinate)

    def tick(self, time_delta: Millisecond) -> Self:
        return self

    @property
    def is_complete(self) -> bool:
        return True
