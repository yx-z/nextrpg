from typing import TYPE_CHECKING, Self

from nextrpg.core.time import Millisecond
from nextrpg.geometry.sizable import Sizable

if TYPE_CHECKING:
    from nextrpg.drawing.drawing_on_screen import DrawingOnScreen


class AnimationOnScreenLike(Sizable):
    drawing_on_screen: DrawingOnScreen
    drawing_on_screens: tuple[DrawingOnScreen, ...]

    def tick(self, time_delta: Millisecond) -> Self:
        return self

    @property
    def is_complete(self) -> bool:
        return True
