from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self

from nextrpg.core.color import Color
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Height, Size, Width
from nextrpg.core.sizable import Sizable
from nextrpg.draw.drawing_on_screen import DrawingOnScreen


class AreaOnScreen(Sizable, ABC):
    points: tuple[Coordinate, ...]

    @abstractmethod
    def fill(
        self, color: Color, allow_background_in_debug: bool = True
    ) -> DrawingOnScreen: ...

    @abstractmethod
    def collide(self, area: AreaOnScreen) -> bool: ...

    @abstractmethod
    def __contains__(self, coordinate: Coordinate) -> bool: ...

    @abstractmethod
    def __add__(self, other: Coordinate | Size | Width | Height) -> Self: ...

    def __sub__(self, other: Coordinate | Size | Width | Height) -> Self:
        return self + -other
