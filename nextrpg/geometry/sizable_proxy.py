from dataclasses import dataclass
from functools import cached_property

from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.scaling import WidthAndHeightScaling
from nextrpg.geometry.sizable import Sizable
from nextrpg.geometry.size import Size


@dataclass(frozen=True)
class _SizableProxy:
    size_input: Sizable | Size

    @cached_property
    def size(self) -> Size:
        if isinstance(self.size_input, Size):
            return self.size_input
        return self.size_input.size


@dataclass(frozen=True)
class TopLeftSizable(_SizableProxy, Sizable):
    top_left: Coordinate


@dataclass(frozen=True)
class TopCenterSizable(_SizableProxy, Sizable):
    top_center_input: Coordinate

    @cached_property
    def top_left(self) -> Coordinate:
        return self.top_center_input - self.width / 2


@dataclass(frozen=True)
class TopRightSizable(_SizableProxy, Sizable):
    top_right_input: Coordinate

    @cached_property
    def top_left(self) -> Coordinate:
        return self.top_right_input - self.width


@dataclass(frozen=True)
class CenterLeftSizable(_SizableProxy, Sizable):
    center_left_input: Coordinate

    @cached_property
    def top_left(self) -> Coordinate:
        return self.center_left_input - self.height / 2


@dataclass(frozen=True)
class CenterSizable(_SizableProxy, Sizable):
    center_input: Coordinate

    @cached_property
    def top_left(self) -> Coordinate:
        return self.center_input - self.size / WidthAndHeightScaling(2)


@dataclass(frozen=True)
class CenterRightSizable(_SizableProxy, Sizable):
    center_right_input: Coordinate

    @cached_property
    def top_left(self) -> Coordinate:
        return self.center_right_input - self.height / 2 - self.width


@dataclass(frozen=True)
class BottomLeftSizable(_SizableProxy, Sizable):
    bottom_left_input: Coordinate

    @cached_property
    def top_left(self) -> Coordinate:
        return self.bottom_left_input - self.height


@dataclass(frozen=True)
class BottomCenterSizable(_SizableProxy, Sizable):
    bottom_center_input: Coordinate

    @cached_property
    def top_left(self) -> Coordinate:
        return self.bottom_center_input - self.height - self.width / 2


@dataclass(frozen=True)
class BottomRightSizable(_SizableProxy, Sizable):
    bottom_right_input: Coordinate

    @cached_property
    def top_left(self) -> Coordinate:
        return self.bottom_right_input - self.size
