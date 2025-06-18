from contextlib import contextmanager
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Generator

from pygame import Surface

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.config import Config, config, set_config
from nextrpg.core import (
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
    data: str = ""

    def get_width(self) -> int:
        return 1

    def get_height(self) -> int:
        return 2

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


@contextmanager
def override_config(cfg: Config) -> Generator[Config, None, None]:
    previous_config = config()
    try:
        yield set_config(cfg)
    finally:
        set_config(previous_config)
