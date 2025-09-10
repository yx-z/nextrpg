from typing import NamedTuple, Self

type Alpha = int


class Color(NamedTuple):
    red: int
    green: int
    blue: int
    alpha: Alpha = 255

    @property
    def save_data(self) -> list[int]:
        return list(self)

    @classmethod
    def load(cls, data: list[int]) -> Self:
        return cls(*data)


RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
TRANSPARENT = Color(0, 0, 0, 0)


def alpha_from_percentage(percentage: float) -> Alpha:
    return int(255 * percentage)
