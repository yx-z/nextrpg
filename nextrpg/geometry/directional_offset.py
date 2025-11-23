from dataclasses import dataclass, replace
from functools import cached_property
from math import cos, radians, sin
from typing import Self

from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Pixel, ValueScaling
from nextrpg.geometry.direction import Direction
from nextrpg.geometry.size import Size

type Degree = int | float
type Radian = float


@dataclass(frozen=True)
class DirectionalOffset:
    direction: Direction | Degree
    offset: Pixel

    @cached_property
    def directional_offset(self) -> Self:
        return self

    def __mul__(self, scaling: ValueScaling) -> Self:
        return replace(self, offset=self.offset * scaling)

    def __rmul__(self, scaling: ValueScaling) -> Self:
        return self * scaling

    def __truediv__(self, scaling: ValueScaling) -> Self:
        return self * (1.0 / scaling)

    @cached_property
    def coordinate(self) -> Coordinate:
        return self.size.coordinate

    @cached_property
    def size(self) -> Size:
        width = cos(self.radian) * self.offset
        height = sin(self.radian) * self.offset
        return Size(width, height)

    @cached_property
    def radian(self) -> Radian:
        return radians(self.degree)

    @cached_property
    def degree(self) -> Degree:
        if isinstance(self.direction, int | float):
            return self.direction

        match self.direction:
            case Direction.DOWN:
                return 90
            case Direction.LEFT:
                return 180
            case Direction.RIGHT:
                return 0
            case Direction.UP:
                return 270
            case Direction.UP_LEFT:
                return 225
            case Direction.UP_RIGHT:
                return 315
            case Direction.DOWN_LEFT:
                return 135
            case Direction.DOWN_RIGHT:
                return 45

    def __neg__(self) -> Self:
        offset = -self.offset
        return replace(self, offset=offset)
