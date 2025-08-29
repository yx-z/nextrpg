from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple, Self, overload

if TYPE_CHECKING:
    from nextrpg.geometry.coordinate import Coordinate

type Pixel = int | float

type PixelPerMillisecond = int | float


@dataclass(frozen=True)
class _Dimension:
    value: Pixel

    def __lt__(self, other: Self) -> bool:
        return self.value < other.value

    def __le__(self, other: Self) -> bool:
        return self.value <= other.value

    def __neg__(self) -> Self:
        return type(self)(-self.value)

    def __add__(self, other: Self) -> Self:
        return type(self)(self.value + other.value)

    def __sub__(self, other: Self) -> Self:
        return self + -other


class _Scaling(_Dimension):
    @property
    def complement(self) -> Self:
        return type(self)(1.0 - self.value)


class WidthScaling(_Scaling):
    pass


class HeightScaling(_Scaling):
    pass


class WidthAndHeightScaling(_Scaling):
    pass


class Width(_Dimension):
    @overload
    def __mul__(self, arg: int | float | WidthScaling) -> Width: ...

    @overload
    def __mul__(self, arg: Height) -> Size: ...

    def __mul__(self, arg: int | float | WidthScaling | Height) -> Width | Size:
        if isinstance(arg, Height):
            return Size(self.value, arg.value)
        if isinstance(arg, int | float):
            return Width(self.value * arg)
        return Width(self.value * arg.value)

    def __rmul__(self, arg: int | float | WidthScaling) -> Width:
        return Width(self.value * arg)

    @overload
    def __truediv__(self, arg: int | float | WidthScaling) -> Width: ...

    @overload
    def __truediv__(self, arg: Width) -> WidthScaling: ...

    def __truediv__(
        self, arg: int | float | WidthScaling | Width
    ) -> Width | WidthScaling:
        if isinstance(arg, Width):
            return WidthScaling(self.value / arg.value)

        if isinstance(arg, int | float):
            return Width(self.value / arg)
        return Width(self.value / arg.value)

    def with_height(self, height: Height) -> Size:
        return self * height

    @property
    def with_zero_height(self) -> Size:
        return self * Height(0)


class Height(_Dimension):
    @overload
    def __mul__(self, arg: int | float | HeightScaling) -> Height: ...

    @overload
    def __mul__(self, arg: Width) -> Size: ...

    def __mul__(
        self, arg: int | float | HeightScaling | Width
    ) -> Height | Size:
        if isinstance(arg, Width):
            return Size(arg.value, self.value)
        if isinstance(arg, int | float):
            return Height(self.value * arg)
        return Height(self.value * arg.value)

    def __rmul__(self, arg: int | float | HeightScaling) -> Height | Size:
        return Height(self.value * arg)

    @overload
    def __truediv__(self, arg: int | float | HeightScaling) -> Height: ...

    @overload
    def __truediv__(self, arg: Height) -> HeightScaling: ...

    def __truediv__(
        self, arg: int | float | HeightScaling | Height
    ) -> Height | HeightScaling:
        if isinstance(arg, Height):
            return HeightScaling(self.value / arg.value)

        if isinstance(arg, int | float):
            return Height(self.value / arg)
        return Height(self.value / arg.value)

    def with_width(self, width: Width) -> Size:
        return width * self

    @property
    def with_zero_width(self) -> Size:
        return Width(0) * self


class Size(NamedTuple):
    width_value: Pixel
    height_value: Pixel

    @property
    def width(self) -> Width:
        return Width(self.width_value)

    @property
    def height(self) -> Height:
        return Height(self.height_value)

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
        return other + -self

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
        return self * type(scaling)(1.0 / scaling.value)

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
