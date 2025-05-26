from dataclasses import dataclass
from enum import Enum, auto
from math import ceil
from typing import NewType, Protocol

from pygame import Surface

Millesecond = NewType("Millisecond", int)


class Direction(Enum):
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    UP = auto()


type Pixel = int


@dataclass(frozen=True)
class Coordinate:
    left: Pixel
    top: Pixel

    def __mul__(self, scale: float) -> "Coordinate":
        return Coordinate(ceil(self.left * scale), ceil(self.top * scale))


@dataclass(frozen=True)
class Size:
    width: Pixel
    height: Pixel

    def __mul__(self, scale: float) -> "Size":
        return Size(ceil(self.width * scale), ceil(self.height * scale))


class CharacterSprite(Protocol):
    def draw(
        self, time_delta: Millesecond, direction: Direction
    ) -> Surface: ...
