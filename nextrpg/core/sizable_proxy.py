from dataclasses import dataclass

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size, WidthAndHeightScaling
from nextrpg.core.sizable import Sizable


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
