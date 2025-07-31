from collections import namedtuple
from dataclasses import dataclass
from typing import NamedTuple

type Alpha = int


class Color(NamedTuple):
    red: int
    green: int
    blue: int
    alpha: Alpha = 255


BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)


def alpha_from_percentage(percentage: float) -> Alpha:
    return int(255 * percentage)
