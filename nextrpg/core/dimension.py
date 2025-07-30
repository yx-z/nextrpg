from __future__ import annotations

from collections import namedtuple
from math import sqrt

type Pixel = int | float

type PixelPerMillisecond = int | float


class Size(namedtuple("Size", "width height")):
    width: Pixel
    height: Pixel

    def __neg__(self) -> Size:
        return Size(-self.width, -self.height)

    def __add__(self, other: Size) -> Size:
        return Size(self.width + other.width, self.height + other.height)

    def __sub__(self, other: Size) -> Size:
        return self + -other

    def __mul__(self, scaling: float) -> Size:
        dimension_scaling = sqrt(scaling)
        width = self.width * dimension_scaling
        height = self.height * dimension_scaling
        return Size(width, height)

    def __truediv__(self, scaling: float) -> Size:
        return self * (1 / scaling)

    def all_dimension_scale(self, scaling: float) -> Size:
        return Size(self.width * scaling, self.height * scaling)

    def __str__(self) -> str:
        return f"({self.width:.0f}, {self.height:.0f})"
