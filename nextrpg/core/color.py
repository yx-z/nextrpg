from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple, Self, override

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


BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
TRANSPARENT = Color(0, 0, 0, 0)


def alpha_from_percentage(percentage: float) -> Alpha:
    return int(255 * percentage)
