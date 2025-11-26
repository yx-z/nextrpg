from functools import cached_property
from typing import TYPE_CHECKING, NamedTuple, Self, overload, override

from nextrpg.geometry.coordinate import Coordinate, XAxis, YAxis
from nextrpg.geometry.dimension import Dimension, Pixel, ValueScaling
from nextrpg.geometry.scaling import (
    HeightScaling,
    WidthAndHeightScaling,
    WidthScaling,
)

if TYPE_CHECKING:
    from nextrpg.geometry.directional_offset import DirectionalOffset
    from nextrpg.geometry.padding import Padding


class Width(Dimension):
    @cached_property
    def x_axis(self) -> XAxis:
        return XAxis(self.value)

    @overload
    def __mul__(self, other: ValueScaling | WidthScaling) -> Width: ...

    @overload
    def __mul__(self, other: Height) -> Size: ...

    def __mul__(
        self, other: ValueScaling | WidthScaling | Height
    ) -> Width | Size:
        if isinstance(other, Height):
            return Size(self.value, other.value)
        if isinstance(other, int | float):
            return Width(self.value * other)
        return Width(self.value * other.value)

    @overload
    def __truediv__(self, other: ValueScaling | WidthScaling) -> Width: ...

    @overload
    def __truediv__(self, other: Width) -> WidthScaling: ...

    def __truediv__(
        self, other: ValueScaling | WidthScaling | Width
    ) -> Width | WidthScaling:
        if isinstance(other, Width):
            return WidthScaling(self.value / other.value)

        if isinstance(other, int | float):
            return Width(self.value / other)
        return Width(self.value / other.value)

    @cached_property
    def size(self) -> Size:
        return self * ZERO_HEIGHT

    @overload
    def __add__(self, other: int | float | Width) -> Width: ...

    @overload
    def __add__(self, other: Size) -> Size: ...

    def __add__(self, other: int | float | Width | Size) -> Width | Size:
        if isinstance(other, Size):
            return Size(self.value + other.width_value, other.height_value)
        if isinstance(other, Width):
            return Width(self.value + other.value)
        return Width(self.value + other)

    @overload
    def __sub__(self, other: Width) -> Width: ...

    @overload
    def __sub__(self, other: Size) -> Size: ...

    def __sub__(self, other: Width | Size) -> Width | Size:
        return self + -other


class Height(Dimension):
    @cached_property
    def y_axis(self) -> YAxis:
        return YAxis(self.value)

    @overload
    def __mul__(self, other: ValueScaling | HeightScaling) -> Height: ...

    @overload
    def __mul__(self, other: Width) -> Size: ...

    def __mul__(
        self, other: ValueScaling | HeightScaling | Width
    ) -> Height | Size:
        if isinstance(other, Width):
            return Size(other.value, self.value)
        if isinstance(other, int | float):
            return Height(self.value * other)
        return Height(self.value * other.value)

    @overload
    def __truediv__(self, other: ValueScaling | HeightScaling) -> Height: ...

    @overload
    def __truediv__(self, other: Height) -> HeightScaling: ...

    def __truediv__(
        self, other: ValueScaling | HeightScaling | Height
    ) -> Height | HeightScaling:
        if isinstance(other, Height):
            return HeightScaling(self.value / other.value)

        if isinstance(other, int | float):
            return Height(self.value / other)
        return Height(self.value / other.value)

    @cached_property
    def size(self) -> Size:
        return ZERO_WIDTH * self

    @overload
    def __add__(self, other: int | float | Height) -> Height: ...

    @overload
    def __add__(self, other: Size) -> Size: ...

    def __add__(self, other: int | float | Height | Size) -> Height | Size:
        if isinstance(other, Size):
            return Size(other.width_value, self.value + other.height_value)
        if isinstance(other, Height):
            return Height(self.value + other.value)
        return Height(self.value + other)

    @overload
    def __sub__(self, other: Height) -> Height: ...

    @overload
    def __sub__(self, other: Size) -> Size: ...

    def __sub__(self, other: Height | Size) -> Height | Size:
        return self + -other


class Size(NamedTuple):
    width_value: Pixel
    height_value: Pixel

    @property
    def size(self) -> Self:
        return self

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

    def __add__(
        self, other: Coordinate | Width | Height | Size | Padding
    ) -> Size:
        if isinstance(other, Size):
            return Size(
                self.width_value + other.width_value,
                self.height_value + other.height_value,
            )
        return (other + self).size

    def __sub__(
        self, other: Coordinate | Width | Height | Size | Padding
    ) -> Size:
        return self + -other

    def __mul__(
        self,
        scaling: (
            ValueScaling | WidthScaling | HeightScaling | WidthAndHeightScaling
        ),
    ) -> Size:
        if isinstance(scaling, WidthScaling):
            return Size(self.width_value * scaling.value, self.height_value)

        if isinstance(scaling, HeightScaling):
            return Size(self.width_value, self.height_value * scaling.value)

        if isinstance(scaling, WidthAndHeightScaling):
            value = scaling.value
        else:
            value = scaling
        return Size(self.width_value * value, self.height_value * value)

    def __rmul__(
        self,
        scaling: (
            ValueScaling | WidthScaling | HeightScaling | WidthAndHeightScaling
        ),
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
        return Coordinate(self.width_value, self.height_value)

    @property
    def save_data(self) -> Self:
        return self

    @classmethod
    def load_from_save(cls, data: list[Pixel]) -> Self:
        assert len(data) == 2, f"Size only takes [left, top]. Got {data}."
        return cls(*data)

    @property
    def directional_offset(self) -> DirectionalOffset:
        return self.coordinate.directional_offset


ZERO_WIDTH = Width(0)
ZERO_HEIGHT = Height(0)
ZERO_SIZE = Size(0, 0)
