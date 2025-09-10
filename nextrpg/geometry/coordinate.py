from __future__ import annotations

from math import atan2, degrees, hypot
from typing import TYPE_CHECKING, NamedTuple, Self, overload

from nextrpg.core.save import module_and_class
from nextrpg.geometry.dimension import Dimension, Height, Pixel, Size, Width
from nextrpg.geometry.direction import Direction, DirectionalOffset

if TYPE_CHECKING:
    from nextrpg.geometry.sizable_proxy import (
        BottomCenterSizable,
        BottomLeftSizable,
        BottomRightSizable,
        CenterLeftSizable,
        CenterRightSizable,
        CenterSizable,
        Sizable,
        TopCenterSizable,
        TopLeftSizable,
        TopRightSizable,
    )


class XAxis(Dimension):
    @property
    def width(self) -> Width:
        return Width(self.value)

    def __add__(self, other: Pixel | Width) -> XAxis:
        if isinstance(other, Width):
            return XAxis(self.value + other.value)
        return XAxis(self.value + other)

    @overload
    def __sub__(self, other: Pixel | Width) -> XAxis: ...

    @overload
    def __sub__(self, other: XAxis) -> Width: ...

    def __sub__(self, other: Pixel | Width | XAxis) -> XAxis | Width:
        if isinstance(other, XAxis):
            return Width(self.value - other.value)
        if isinstance(other, Width):
            return XAxis(self.value - other.value)
        return XAxis(self.value - other)

    def pair(self, y_axis: YAxis) -> Coordinate:
        return Coordinate(self.value, y_axis.value)

    @property
    def with_zero_y_axis(self) -> Coordinate:
        return self.pair(YAxis(0))


class YAxis(Dimension):
    @property
    def height(self) -> Height:
        return Height(self.value)

    def __add__(self, other: Pixel | Height) -> YAxis:
        if isinstance(other, Height):
            return YAxis(self.value + other.value)
        return YAxis(self.value + other)

    @overload
    def __sub__(self, other: Pixel | Height) -> YAxis: ...

    @overload
    def __sub__(self, other: YAxis) -> Height: ...

    def __sub__(self, other: Pixel | Height | YAxis) -> YAxis | Height:
        if isinstance(other, YAxis):
            return Height(self.value - other.value)
        if isinstance(other, Height):
            return YAxis(self.value - other.value)
        return YAxis(self.value - other)

    def pair(self, x_axis: XAxis) -> Coordinate:
        return Coordinate(x_axis.value, self.value)

    @property
    def with_zero_x_axis(self) -> Coordinate:
        return self.pair(XAxis(0))


class Coordinate(NamedTuple):
    left_value: Pixel
    top_value: Pixel

    @property
    def left(self) -> XAxis:
        return XAxis(self.left_value)

    @property
    def top(self) -> YAxis:
        return YAxis(self.top_value)

    @property
    def size(self) -> Size:
        return self.left.width * self.top.height

    def __neg__(self) -> Coordinate:
        return Coordinate(-self.left_value, -self.top_value)

    def __add__(
        self, arg: Coordinate | DirectionalOffset | Size | Width | Height
    ) -> Coordinate:
        if isinstance(arg, Width):
            return Coordinate(self.left_value + arg.value, self.top_value)

        if isinstance(arg, Height):
            return Coordinate(self.left_value, self.top_value + arg.value)

        if isinstance(arg, Size):
            return Coordinate(
                self.left_value + arg.width_value,
                self.top_value + arg.height_value,
            )

        if isinstance(arg, Coordinate):
            return Coordinate(
                self.left_value + arg.left_value, self.top_value + arg.top_value
            )
        return self + arg.shift

    def __sub__(
        self, arg: DirectionalOffset | Size | Width | Height | Coordinate
    ) -> Coordinate:
        return self + -arg

    def relative_to(self, other: Coordinate) -> Direction:
        dx = self.left_value - other.left_value
        dy = self.top_value - other.top_value
        angle = (degrees(atan2(-dy, dx)) + 360) % 360
        closest = min(
            _ANGLE_TO_DIRECTION.items(),
            key=lambda a: _angle_difference(angle, a[0]),
        )
        return closest[1]

    def __str__(self) -> str:
        return f"({self.left_value:.0f}, {self.top_value:.0f})"

    def __repr__(self) -> str:
        return str(self)

    def distance(self, other: Coordinate) -> Pixel:
        dx = self.left_value - other.left_value
        dy = self.top_value - other.top_value
        return hypot(dx, dy)

    def as_top_left_of(self, sizable: Sizable | Size) -> TopLeftSizable:
        from nextrpg.geometry.sizable_proxy import TopLeftSizable

        return TopLeftSizable(sizable, self)

    def as_top_center_of(self, sizable: Sizable | Size) -> TopCenterSizable:
        from nextrpg.geometry.sizable_proxy import TopCenterSizable

        return TopCenterSizable(sizable, self)

    def as_top_right_of(self, sizable: Sizable | Size) -> TopRightSizable:
        from nextrpg.geometry.sizable_proxy import TopRightSizable

        return TopRightSizable(sizable, self)

    def as_center_left_of(self, sizable: Sizable | Size) -> CenterLeftSizable:
        from nextrpg.geometry.sizable_proxy import CenterLeftSizable

        return CenterLeftSizable(sizable, self)

    def as_center_of(self, sizable: Sizable | Size) -> CenterSizable:
        from nextrpg.geometry.sizable_proxy import CenterSizable

        return CenterSizable(sizable, self)

    def as_center_right_of(self, sizable: Sizable | Size) -> CenterRightSizable:
        from nextrpg.geometry.sizable_proxy import CenterRightSizable

        return CenterRightSizable(sizable, self)

    def as_bottom_left_of(self, sizable: Sizable | Size) -> BottomLeftSizable:
        from nextrpg.geometry.sizable_proxy import BottomLeftSizable

        return BottomLeftSizable(sizable, self)

    def as_bottom_center_of(
        self, sizable: Sizable | Size
    ) -> BottomCenterSizable:
        from nextrpg.geometry.sizable_proxy import BottomCenterSizable

        return BottomCenterSizable(sizable, self)

    def as_bottom_right_of(self, sizable: Sizable | Size) -> BottomRightSizable:
        from nextrpg.geometry.sizable_proxy import BottomRightSizable

        return BottomRightSizable(sizable, self)

    @property
    def save_data(self) -> list[Pixel]:
        return list(self)

    @classmethod
    def save_key(cls) -> str:
        return module_and_class(cls)

    @classmethod
    def load_from_save(cls, data: list[Pixel]) -> Self:
        return cls(*data)

    def anchor(self, size: Size | Sizable) -> TopLeftSizable:
        return self.as_top_left_of(size)


ORIGIN = Coordinate(0, 0)


def _angle_difference(a1: float, a2: float) -> float:
    return abs((a1 - a2 + 180) % 360 - 180)


_ANGLE_TO_DIRECTION = {
    0: Direction.RIGHT,
    45: Direction.UP_RIGHT,
    90: Direction.UP,
    135: Direction.UP_LEFT,
    180: Direction.LEFT,
    225: Direction.DOWN_LEFT,
    270: Direction.DOWN,
    315: Direction.DOWN_RIGHT,
}
