from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, overload

from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Pixel
from nextrpg.geometry.sizable import Sizable
from nextrpg.geometry.size import ZERO_HEIGHT, ZERO_WIDTH, Height, Size, Width


@dataclass(frozen=True)
class Padding:
    top: Height = ZERO_HEIGHT
    left: Width = ZERO_WIDTH
    bottom: Height = ZERO_HEIGHT
    right: Width = ZERO_WIDTH

    def __neg__(self) -> Self:
        return replace(
            self,
            top=-self.top,
            left=-self.left,
            bottom=-self.bottom,
            right=-self.right,
        )

    @overload
    def __add__(self, other: Padding) -> Self: ...

    @overload
    def __add__(self, other: Size) -> Size: ...

    def __add__(self, other: Padding | Size) -> Self | Size:
        if isinstance(other, Padding):
            return replace(
                self,
                top=self.top + other.top,
                left=self.left + other.left,
                bottom=self.bottom + other.bottom,
                right=self.right + other.right,
            )
        return Size(
            self.left.value + other.width.value + self.right.value,
            self.top.value + other.height.value + self.bottom.value,
        )

    @overload
    def __sub__(self, other: Padding) -> Self: ...

    @overload
    def __sub__(self, other: Size) -> Size: ...

    def __sub__(self, other: Padding | Size) -> Self | Size:
        return self + -other

    @cached_property
    def top_left(self) -> Coordinate:
        return (self.top * self.left).coordinate

    @cached_property
    def top_right(self) -> Coordinate:
        return (self.top * self.right).coordinate

    @cached_property
    def bottom_left(self) -> Coordinate:
        return (self.bottom * self.left).coordinate

    @cached_property
    def bottom_right(self) -> Coordinate:
        return (self.bottom * self.right).coordinate

    @cached_property
    def width(self) -> Width:
        return self.left + self.right

    @cached_property
    def height(self) -> Height:
        return self.top + self.bottom


def padding_for_both_sides(width: Width, height: Height) -> Padding:
    return Padding(top=height, left=width, bottom=height, right=width)


def padding_for_all_sides(pixel: Pixel) -> Padding:
    width = Width(pixel)
    height = Height(pixel)
    return padding_for_both_sides(width, height)


def padding_between(smaller: Sizable, bigger: Sizable) -> Padding:
    top = smaller.top - bigger.top
    left = smaller.left - bigger.left
    bottom = bigger.bottom - smaller.bottom
    right = bigger.right - smaller.right
    return Padding(top, left, bottom, right)
