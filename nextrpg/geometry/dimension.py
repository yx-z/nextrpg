from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, NamedTuple, Self, overload, override

from nextrpg.core.save import module_and_class

if TYPE_CHECKING:
    from nextrpg.geometry.coordinate import Coordinate, XAxis, YAxis
    from nextrpg.geometry.padding import Padding

type Pixel = int | float
type PixelPerMillisecond = int | float


@dataclass(frozen=True)
class Dimension:
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

    def __mul__(self, other: int | float) -> Self:
        return type(self)(self.value * other)

    def __rmul__(self, other: int | float) -> Self:
        return self * other

    def __truediv__(self, other: int | float) -> Self:
        return self * (1.0 / other)

    def __rtruediv__(self, other: int | float) -> Self:
        return other * (1.0 / self)


class _Scaling(Dimension):
    @cached_property
    def complement(self) -> Self:
        return type(self)(1.0 - self.value)


class WidthScaling(_Scaling):
    pass


class WidthAndHeightScaling(_Scaling):
    @overload
    def __mul__(self, arg: int | float) -> WidthScaling: ...

    @overload
    def __mul__(self, arg: Width) -> Width: ...

    def __mul__(self, arg: int | float | Width) -> WidthScaling | Width:
        if isinstance(arg, Width):
            return Width(self.value * arg.value)
        return WidthScaling(self.value * arg)


class HeightScaling(_Scaling):
    @overload
    def __mul__(self, arg: int | float) -> HeightScaling: ...

    @overload
    def __mul__(self, arg: Height) -> Height: ...

    def __mul__(self, arg: int | float | Height) -> HeightScaling | Height:
        if isinstance(arg, Height):
            return Height(self.value * arg.value)
        return HeightScaling(self.value * arg)


class Width(Dimension):
    @cached_property
    def x_axis(self) -> XAxis:
        from nextrpg.geometry.coordinate import XAxis

        return XAxis(self.value)

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

    @cached_property
    def zero_height(self) -> Size:
        return self * Height(0)


class Height(Dimension):
    @cached_property
    def y_axis(self) -> YAxis:
        from nextrpg.geometry.coordinate import YAxis

        return YAxis(self.value)

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

    @cached_property
    def zero_width(self) -> Size:
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

    @property
    def negate_width(self) -> Size:
        return Size(-self.width_value, self.height_value)

    @property
    def negate_height(self) -> Size:
        return Size(self.width_value, -self.height_value)

    def __neg__(self) -> Size:
        return Size(-self.width_value, -self.height_value)

    def __add__(self, other: Size | Width | Height | Padding) -> Size:
        from nextrpg.geometry.padding import Padding

        if isinstance(other, Padding):
            return Size(
                self.width_value + other.left.value + other.right.value,
                self.height_value + other.top.value + other.bottom.value,
            )

        if isinstance(other, Width):
            return Size(self.width_value + other.value, self.height_value)

        if isinstance(other, Height):
            return Size(self.width_value, self.height_value + other.value)

        return Size(
            self.width_value + other.width_value,
            self.height_value + other.height_value,
        )

    def __radd__(self, other: Size | Width | Height | Padding) -> Size:
        return self + other

    def __sub__(self, other: Size | Width | Height | Padding) -> Size:
        return self + -other

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

    @override
    def __str__(self) -> str:
        return f"({self.width_value:.0f}, {self.height_value:.0f})"

    @override
    def __repr__(self) -> str:
        return str(self)

    @property
    def coordinate(self) -> Coordinate:
        from nextrpg.geometry.coordinate import Coordinate

        return Coordinate(self.width_value, self.height_value)

    @classmethod
    def save_key(cls) -> str:
        return module_and_class(cls)

    @property
    def save_data(self) -> list[Pixel]:
        return list(self)

    @classmethod
    def load_from_save(cls, data: list[Pixel]) -> Self:
        return cls(*data)


ZERO_SIZE = Size(0, 0)
