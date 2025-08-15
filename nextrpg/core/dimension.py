from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Self, override

from nextrpg.core.save import LoadFromSaveList

type Pixel = int | float

type PixelPerMillisecond = int | float


@dataclass(frozen=True)
class _Dimension:
    input_value: Pixel | _Dimension

    def __lt__(self, other: Self) -> bool:
        return self.value < other.value

    def __le__(self, other: Self) -> bool:
        return self.value <= other.value

    @property
    def value(self) -> Pixel:
        if isinstance(self.input_value, _Dimension):
            return self.input_value.value
        return self.input_value

    def __neg__(self) -> Self:
        return type(self)(-self.value)

    def __add__(self, other: Self | Pixel) -> Self:
        if isinstance(other, _Dimension):
            return type(self)(self.value + other.value)
        return type(self)(self.value + other)

    def __radd__(self, other: Self | Pixel) -> Self:
        return self + other

    def __sub__(self, other: Self | Pixel) -> Self:
        return self + -other

    def __rsub__(self, other: Self | Pixel) -> Self:
        return -self + other

    def __mul__(self, scaling: int | float) -> Self:
        return type(self)(self.value * scaling)

    def __rmul__(self, scaling: int | float) -> Self:
        return self * scaling

    def __truediv__(self, scaling: int | float) -> Self:
        return self * (1 / scaling)


class Width(_Dimension):
    @override
    def __mul__(self, scaling: int | float | WidthScaling) -> Width:
        if isinstance(scaling, WidthScaling):
            return Width(self.value * scaling.value)
        return Width(self.value * scaling)

    @override
    def __truediv__(self, scaling: int | float | WidthScaling) -> Width:
        if isinstance(scaling, WidthScaling):
            return self * (1 / scaling.value)
        return self * (1 / scaling)


class Height(_Dimension):
    @override
    def __mul__(self, scaling: int | float | HeightScaling) -> Height:
        if isinstance(scaling, HeightScaling):
            return Height(self.value * scaling.value)
        return Height(self.value * scaling)

    @override
    def __rmul__(self, scaling: int | float | HeightScaling) -> Height:
        return self * scaling

    @override
    def __truediv__(self, scaling: int | float | HeightScaling) -> Height:
        if isinstance(scaling, HeightScaling):
            return self * (1 / scaling.value)
        return self * (1 / scaling)


class WidthScaling(_Dimension):
    pass


class HeightScaling(_Dimension):
    pass


class WidthAndHeightScaling(_Dimension):
    pass


@dataclass(frozen=True)
class Size(LoadFromSaveList[int]):
    input_width: Pixel | Width
    input_height: Pixel | Height

    @property
    def width(self) -> Width:
        if isinstance(self.input_width, Width):
            return self.input_width
        return Width(self.input_width)

    @property
    def height(self) -> Height:
        if isinstance(self.input_height, Height):
            return self.input_height
        return Height(self.input_height)

    @property
    def tuple(self) -> tuple[Pixel, Pixel]:
        return self.width.value, self.height.value

    def __iter__(self) -> Iterator[Width | Height]:
        return iter((self.width, self.height))

    def __neg__(self) -> Size:
        return Size(-self.width, -self.height)

    def __add__(self, other: Size | Width | Height) -> Size:
        if isinstance(other, Width):
            return Size(self.width + other, self.height)

        if isinstance(other, Height):
            return Size(self.width, self.height + other)

        return Size(self.width + other.width, self.height + other.height)

    def __radd__(self, other: Size | Width | Height) -> Size:
        return self + other

    def __sub__(self, other: Size | Width | Height) -> Size:
        return self + -other

    def __rsub__(self, other: Size | Width | Height) -> Size:
        return -self + other

    def __mul__(
        self, scaling: WidthScaling | HeightScaling | WidthAndHeightScaling
    ) -> Size:
        if isinstance(scaling, WidthScaling):
            return Size(self.width * scaling, self.height)

        if isinstance(scaling, HeightScaling):
            return Size(self.width, self.height * scaling)
        return Size(self.width * scaling.value, self.height * scaling.value)

    def __rmul__(
        self, scaling: WidthScaling | HeightScaling | WidthAndHeightScaling
    ) -> Size:
        return self * scaling

    def __truediv__(
        self, scaling: WidthScaling | HeightScaling | WidthAndHeightScaling
    ) -> Size:
        return self * type(scaling)(1 / scaling.value)

    def __repr__(self) -> str:
        return f"({self.width.value:.0f}, {self.height.value:.0f})"

    @override
    def save(self) -> list[int]:
        return list(self.tuple)
