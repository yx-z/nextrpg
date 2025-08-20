from dataclasses import dataclass
from typing import Protocol

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Height, Size, Width, WidthAndHeightScaling


class Sizable(Protocol):
    # Subclass shall implement these.
    top_left: Coordinate
    size: Size

    @property
    def width(self) -> Width:
        return self.size.width

    @property
    def height(self) -> Height:
        return self.size.height

    @property
    def top(self) -> Height:
        return self.top_left.top

    @property
    def left(self) -> Width:
        return self.top_left.left

    @property
    def bottom(self) -> Height:
        return self.top_left.top + self.size.height

    @property
    def right(self) -> Width:
        return self.top_left.left + self.size.width

    @property
    def top_right(self) -> Coordinate:
        return self.top_left + self.width

    @property
    def bottom_left(self) -> Coordinate:
        return self.top_left + self.height

    @property
    def bottom_right(self) -> Coordinate:
        return self.top_left + self.size

    @property
    def top_center(self) -> Coordinate:
        return self.top_left + self.width / 2

    @property
    def bottom_center(self) -> Coordinate:
        return self.top_left + self.height / 2

    @property
    def center_left(self) -> Coordinate:
        return self.top_left + self.height / 2

    @property
    def center_right(self) -> Coordinate:
        return self.top_right + self.height / 2

    @property
    def center(self) -> Coordinate:
        return self.top_center + self.height / 2


@dataclass(frozen=True)
class SizableProxy(Sizable):
    sizable: Sizable

    @property
    def size(self) -> Size:
        return self.sizable.size


@dataclass(frozen=True)
class TopLeft(SizableProxy):
    top_left: Coordinate


@dataclass(frozen=True)
class TopCenter(SizableProxy):
    top_center_input: Coordinate

    @property
    def top_left(self) -> Coordinate:
        return self.top_center_input - self.width / 2


@dataclass(frozen=True)
class TopRight(SizableProxy):
    top_right_input: Coordinate

    @property
    def top_left(self) -> Coordinate:
        return self.top_right_input - self.width


@dataclass(frozen=True)
class CenterLeft(SizableProxy):
    center_left_input: Coordinate

    @property
    def top_left(self) -> Coordinate:
        return self.center_left_input - self.height / 2


@dataclass(frozen=True)
class Center(SizableProxy):
    center_input: Coordinate

    @property
    def top_left(self) -> Coordinate:
        return self.center_input - self.size / WidthAndHeightScaling(2)


@dataclass(frozen=True)
class CenterRight(SizableProxy):
    center_right_input: Coordinate

    @property
    def top_left(self) -> Coordinate:
        return self.center_right_input - self.height / 2 - self.width


@dataclass(frozen=True)
class BottomLeft(SizableProxy):
    bottom_left_input: Coordinate

    @property
    def top_left(self) -> Coordinate:
        return self.bottom_left_input - self.height


@dataclass(frozen=True)
class BottomCenter(SizableProxy):
    bottom_center_input: Coordinate

    @property
    def top_left(self) -> Coordinate:
        return self.bottom_center_input - self.height - self.width / 2


@dataclass(frozen=True)
class BottomRight(SizableProxy):
    bottom_right_input: Coordinate

    def top_left(self) -> Coordinate:
        return self.bottom_right_input - self.size
