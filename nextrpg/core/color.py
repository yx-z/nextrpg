from __future__ import annotations

from dataclasses import dataclass

type Alpha = int


@dataclass(frozen=True)
class Color:
    red: int
    green: int
    blue: int
    alpha: Alpha = 255

    @property
    def tuple(self) -> tuple[int, int, int, Alpha]:
        return self.red, self.green, self.blue, self.alpha


BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
TRANSPARENT = Color(0, 0, 0, 0)


def alpha_from_percentage(percentage: float) -> Alpha:
    return int(255 * percentage)
