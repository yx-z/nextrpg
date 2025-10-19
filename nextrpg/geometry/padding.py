from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self

from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Height, Pixel, Size, Width


@dataclass(frozen=True)
class Padding:
    top: Height = Height(0)
    left: Width = Width(0)
    bottom: Height = Height(0)
    right: Width = Width(0)

    def __neg__(self) -> Self:
        return replace(
            self,
            top=-self.top,
            left=-self.left,
            bottom=-self.bottom,
            right=-self.right,
        )

    @cached_property
    def top_left(self) -> Coordinate:
        return self.top_left_shift.coordinate

    @cached_property
    def top_left_shift(self) -> Size:
        return self.top * self.left


def padding_for_both_sides(width: Width, height: Height) -> Padding:
    return Padding(top=height, left=width, bottom=height, right=width)


def padding_for_all_sides(pixel: Pixel) -> Padding:
    width = Width(pixel)
    height = Height(pixel)
    return padding_for_both_sides(width, height)
