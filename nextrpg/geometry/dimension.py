from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple, Self, overload, override

if TYPE_CHECKING:
    from nextrpg.geometry.coordinate import Coordinate

type Pixel = int | float

type PixelPerMillisecond = int | float


@dataclass(frozen=True)
class _Dimension:
    value: Pixel

    def __lt__(self, other: Self | Pixel) -> bool:
        if isinstance(other, _Dimension):
            return self.value < other.value
        return self.value < other

    def __le__(self, other: Self | Pixel) -> bool:
        if isinstance(other, _Dimension):
            return self.value <= other.value
        return self.value <= other

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


class WidthScaling(_Dimension):
    pass


class HeightScaling(_Dimension):
    pass


class WidthAndHeightScaling(_Dimension):
    pass


class Width(_Dimension):
    @overload
    def __mul__(self, arg: int | float | WidthScaling) -> Width: ...

    @overload
    def __mul__(self, arg: Height) -> Size: ...

    @override
    def __mul__(self, arg: int | float | WidthScaling | Height) -> Width | Size:
        if isinstance(arg, Height):
            return Size(self.value, arg.value)
        if isinstance(arg, WidthScaling):
            return Width(self.value * arg.value)
        return Width(self.value * arg)

    @override
    def __rmul__(self, arg: int | float | WidthScaling) -> Width:
        return self * arg

    @override
    def __truediv__(self, arg: int | float | WidthScaling) -> Width:
        if isinstance(arg, WidthScaling):
            return self * (1 / arg.value)
        return self * (1 / arg)


class Height(_Dimension):
    @overload
    def __mul__(self, arg: int | float | HeightScaling) -> Height: ...

    @overload
    def __mul__(self, arg: Width) -> Size: ...

    @override
    def __mul__(
        self, arg: int | float | HeightScaling | Width
    ) -> Height | Size:
        if isinstance(arg, Width):
            return Size(arg.value, self.value)
        if isinstance(arg, HeightScaling):
            return Height(self.value * arg.value)
        return Height(self.value * arg)

    @override
    def __rmul__(self, arg: int | float | HeightScaling) -> Height | Size:
        return self * arg

    @override
    def __truediv__(self, scaling: int | float | HeightScaling) -> Height:
        if isinstance(scaling, HeightScaling):
            return self * (1 / scaling.value)
        return self * (1 / scaling)


class Size(NamedTuple):
    width_value: Pixel
    height_value: Pixel

    @property
    def width(self) -> Width:
        return Width(self.width_value)

    @property
    def height(self) -> Height:
        return Height(self.height_value)

    @property
    def negate_width(self) -> Size:
        return Size(-self.width_value, self.height_value)

    @property
    def negate_height(self) -> Size:
        return Size(self.width_value, -self.height_value)

    def __neg__(self) -> Size:
        return Size(-self.width_value, -self.height_value)

    def __add__(self, other: Size | Width | Height) -> Size:
        if isinstance(other, Width):
            return Size(self.width_value + other.value, self.height_value)

        if isinstance(other, Height):
            return Size(self.width_value, self.height_value + other.value)

        return Size(
            self.width_value + other.width_value,
            self.height_value + other.height_value,
        )

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
            return Size(self.width_value * scaling.value, self.height_value)

        if isinstance(scaling, HeightScaling):
            return Size(self.width_value, self.height_value * scaling.value)

        return Size(
            self.width_value * scaling.value, self.height_value * scaling.value
        )

    def __rmul__(
        self, scaling: WidthScaling | HeightScaling | WidthAndHeightScaling
    ) -> Size:
        return self * scaling

    def __truediv__(
        self, scaling: WidthScaling | HeightScaling | WidthAndHeightScaling
    ) -> Size:
        return self * type(scaling)(1 / scaling.value)

    def __repr__(self) -> str:
        return f"({self.width_value:.0f}, {self.height_value:.0f})"

    @property
    def coordinate(self) -> Coordinate:
        from nextrpg.geometry.coordinate import Coordinate

        return Coordinate(self.width_value, self.height_value)

    @property
    def save_data(self) -> list[Pixel]:
        return list(self)

    @classmethod
    def load(cls, data: list[Pixel]) -> Self:
        return cls(*data)


ZERO_SIZE = Size(0, 0)
