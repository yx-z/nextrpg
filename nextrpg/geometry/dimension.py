from dataclasses import dataclass
from typing import Self

type Pixel = int | float
type PixelPerMillisecond = int | float
type ValueScaling = int | float
type Percentage = float


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

    def __mul__(self, other: ValueScaling) -> Self:
        return type(self)(self.value * other)

    def __rmul__(self, other: ValueScaling) -> Self:
        return self * other

    def __truediv__(self, other: ValueScaling) -> Self:
        return self * (1.0 / other)

    def __rtruediv__(self, other: ValueScaling) -> Self:
        return other * (1.0 / self)
