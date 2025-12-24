from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

from nextrpg.drawing.color import Color
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.sizable import Sizable
from nextrpg.geometry.size import Height, Size, Width

if TYPE_CHECKING:
    from nextrpg.drawing.drawing_on_screen import DrawingOnScreen


class AreaOnScreen(Sizable, ABC):
    points: tuple[Coordinate, ...]

    @abstractmethod
    def fill(
        self, color: Color, allow_background_in_debug: bool = True
    ) -> DrawingOnScreen: ...

    @abstractmethod
    def collide(self, area: AreaOnScreen) -> bool: ...

    @abstractmethod
    def __contains__(self, other: Coordinate | AreaOnScreen) -> bool: ...

    @abstractmethod
    def __add__(self, other: Coordinate | Size | Width | Height) -> Self: ...

    def __sub__(self, other: Coordinate | Size | Width | Height) -> Self:
        return self + -other
