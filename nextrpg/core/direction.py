from __future__ import annotations

from dataclasses import dataclass, replace
from enum import auto
from typing import Self

from nextrpg.core.dimension import Pixel
from nextrpg.core.save import LoadFromSaveEnum


class Direction(LoadFromSaveEnum):
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    UP_LEFT = auto()
    UP_RIGHT = auto()
    DOWN_LEFT = auto()
    DOWN_RIGHT = auto()

    def __neg__(self) -> Direction:
        return _OPPOSITE_DIRECTION[self]


_OPPOSITE_DIRECTION = {
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
    Direction.UP: Direction.DOWN,
    Direction.UP_LEFT: Direction.DOWN_RIGHT,
    Direction.UP_RIGHT: Direction.DOWN_LEFT,
    Direction.DOWN_LEFT: Direction.UP_RIGHT,
    Direction.DOWN_RIGHT: Direction.UP_LEFT,
}


@dataclass(frozen=True)
class DirectionalOffset:
    direction: Direction
    offset: Pixel

    def __neg__(self) -> Self:
        return replace(self, direction=-self.direction)
