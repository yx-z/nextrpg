from collections import namedtuple
from dataclasses import dataclass

type Alpha = int


class Color(
    namedtuple("Color", "red green blue alpha", defaults=(255,)),
):
    red: int
    green: int
    blue: int
    alpha: Alpha = 255


BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)


def alpha_from_percentage(percentage: float) -> Alpha:
    return int(255 * percentage)
