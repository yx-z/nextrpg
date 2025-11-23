from functools import cached_property
from typing import TYPE_CHECKING, Self, overload

from nextrpg.geometry.dimension import Dimension, ValueScaling

if TYPE_CHECKING:
    from nextrpg.geometry.size import Height, Size, Width


class Scaling(Dimension):
    @cached_property
    def complement(self) -> Self:
        return type(self)(1.0 - self.value)


class WidthScaling(Scaling):
    @overload
    def __mul__(self, other: ValueScaling) -> WidthScaling: ...

    @overload
    def __mul__(self, other: Width) -> Width: ...

    def __mul__(self, other: ValueScaling | Width) -> WidthScaling | Width:
        from nextrpg.geometry.size import Width

        if isinstance(other, Width):
            return Width(self.value * other.value)
        return WidthScaling(self.value * other)


class HeightScaling(Scaling):
    @overload
    def __mul__(self, other: ValueScaling) -> HeightScaling: ...

    @overload
    def __mul__(self, other: Height) -> Height: ...

    def __mul__(self, other: ValueScaling | Height) -> HeightScaling | Height:
        from nextrpg.geometry.size import Height

        if isinstance(other, Height):
            return Height(self.value * other.value)
        return HeightScaling(self.value * other)


class WidthAndHeightScaling(Scaling):
    @overload
    def __mul__(self, other: ValueScaling) -> WidthAndHeightScaling: ...

    @overload
    def __mul__(self, other: Size) -> Size: ...

    def __mul__(
        self, other: ValueScaling | Size
    ) -> WidthAndHeightScaling | Size:
        from nextrpg.geometry.size import Size

        if isinstance(other, Size):
            return Size(
                self.value * other.width_value, self.value * other.height_value
            )
        return WidthAndHeightScaling(self.value * other)
