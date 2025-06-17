from dataclasses import dataclass, replace
from functools import cached_property

from pygame import Surface

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.common_types import (
    Direction,
    Millisecond,
)
from nextrpg.draw_on_screen import Drawing


@dataclass(frozen=True)
class MockColor:
    r: int
    g: int
    b: int
    a: int


@dataclass(frozen=True)
class MockSurface(Surface):
    data: str
    width: int = 1
    height: int = 1

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def get_at(self, _: tuple[int, int]) -> MockColor:
        return MockColor(0, 0, 0, 0)


@dataclass(frozen=True)
class MockCharacterDrawing(CharacterDrawing):
    _direction: Direction = Direction.DOWN

    @cached_property
    def direction(self) -> Direction:
        return self._direction

    @cached_property
    def drawing(self) -> Drawing:
        return Drawing(MockSurface("a"))

    def turn(self, direction: Direction) -> "CharacterDrawing":
        return replace(self, _direction=direction)

    def move(self, time_delta: Millisecond) -> "CharacterDrawing":
        return self

    def idle(self, time_delta: Millisecond) -> "CharacterDrawing":
        return self
