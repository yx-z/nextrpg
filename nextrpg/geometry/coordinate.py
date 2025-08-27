from __future__ import annotations

from math import atan2, degrees, hypot, sqrt
from typing import TYPE_CHECKING, NamedTuple, Self

from nextrpg.geometry.dimension import Height, Pixel, Size, Width
from nextrpg.geometry.direction import Direction, DirectionalOffset

if TYPE_CHECKING:
    from nextrpg.geometry.sizable_proxy import (
        BottomCenter,
        BottomLeft,
        BottomRight,
        Center,
        CenterLeft,
        CenterRight,
        Sizable,
        TopCenter,
        TopLeft,
        TopRight,
    )


class Coordinate(NamedTuple):
    left_value: Pixel
    top_value: Pixel

    @property
    def left(self) -> Width:
        return Width(self.left_value)

    @property
    def top(self) -> Height:
        return Height(self.top_value)

    @property
    def size(self) -> Size:
        return Size(self.left_value, self.top_value)

    @property
    def negate_left(self) -> Coordinate:
        return Coordinate(-self.left_value, self.top_value)

    @property
    def negate_top(self) -> Coordinate:
        return Coordinate(self.left_value, -self.top_value)

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

        match arg.direction:
            case Direction.UP:
                return Coordinate(self.left_value, self.top_value - arg.offset)
            case Direction.DOWN:
                return Coordinate(self.left_value, self.top_value + arg.offset)
            case Direction.LEFT:
                return Coordinate(self.left_value - arg.offset, self.top_value)
            case Direction.RIGHT:
                return Coordinate(self.left_value + arg.offset, self.top_value)

        diag = arg.offset / sqrt(2)
        match arg.direction:
            case Direction.UP_LEFT:
                return Coordinate(self.left_value - diag, self.top_value - diag)
            case Direction.UP_RIGHT:
                return Coordinate(self.left_value + diag, self.top_value - diag)
            case Direction.DOWN_LEFT:
                return Coordinate(self.left_value - diag, self.top_value + diag)
            case Direction.DOWN_RIGHT:
                return Coordinate(self.left_value + diag, self.top_value + diag)

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

    def __repr__(self) -> str:
        return f"({self.left_value:.0f}, {self.top_value:.0f})"

    def distance(self, other: Coordinate) -> Pixel:
        dx = self.left_value - other.left_value
        dy = self.top_value - other.top_value
        return hypot(dx, dy)

    def as_top_left_of(self, sizable: Sizable) -> TopLeft:
        from nextrpg.geometry.sizable_proxy import TopLeft

        return TopLeft(sizable, self)

    def as_top_center_of(self, sizable: Sizable) -> TopCenter:
        from nextrpg.geometry.sizable_proxy import TopCenter

        return TopCenter(sizable, self)

    def as_top_right_of(self, sizable: Sizable) -> TopRight:
        from nextrpg.geometry.sizable_proxy import TopRight

        return TopRight(sizable, self)

    def as_center_left_of(self, sizable: Sizable) -> CenterLeft:
        from nextrpg.geometry.sizable_proxy import CenterLeft

        return CenterLeft(sizable, self)

    def as_center_of(self, sizable: Sizable) -> Center:
        from nextrpg.geometry.sizable_proxy import Center

        return Center(sizable, self)

    def as_center_right_of(self, sizable: Sizable) -> CenterRight:
        from nextrpg.geometry.sizable_proxy import CenterRight

        return CenterRight(sizable, self)

    def as_bottom_left_of(self, sizable: Sizable) -> BottomLeft:
        from nextrpg.geometry.sizable_proxy import BottomLeft

        return BottomLeft(sizable, self)

    def as_bottom_center_of(self, sizable: Sizable) -> BottomCenter:
        from nextrpg.geometry.sizable_proxy import BottomCenter

        return BottomCenter(sizable, self)

    def as_bottom_right_of(self, sizable: Sizable) -> BottomRight:
        from nextrpg.geometry.sizable_proxy import BottomRight

        return BottomRight(sizable, self)

    @property
    def save_data(self) -> list[Pixel]:
        return list(self)

    @classmethod
    def load(cls, data: list[Pixel]) -> Self:
        return cls(*data)


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
