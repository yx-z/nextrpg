from collections import namedtuple

type Alpha = int


class Rgb(namedtuple("Rgb", "red green blue")):
    red: int
    green: int
    blue: int


class Rgba(namedtuple("Rgba", "red green blue alpha")):
    red: int
    green: int
    blue: int
    alpha: Alpha


BLACK = Rgba(0, 0, 0, 255)
WHITE = Rgba(255, 255, 255, 255)


def alpha_from_percentage(percentage: float) -> Alpha:
    return int(255 * percentage)
