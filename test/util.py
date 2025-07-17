from contextlib import contextmanager
from dataclasses import dataclass, replace
from functools import cached_property
from types import SimpleNamespace
from typing import Any, Generator, NamedTuple, Self

from pygame import Surface

from nextrpg import (
    CharacterDrawing,
    Config,
    Coordinate,
    Direction,
    Drawing,
    Millisecond,
    config,
    set_config,
)


class MockColor(NamedTuple):
    r: int
    g: int
    b: int
    a: int


@dataclass(frozen=True)
class MockSurface(Surface):
    data: str = ""

    def set_alpha(self, *_: Any) -> Self:
        return self

    def copy(self) -> Self:
        return self

    def get_bounding_rect(self) -> SimpleNamespace:
        return SimpleNamespace(x=0, y=0, width=self.width, height=self.height)

    @property
    def width(self) -> int:
        return 2

    @property
    def height(self) -> int:
        return 2

    def blits(self, iterable: Any) -> None:
        pass


@dataclass(frozen=True)
class MockCharacterDrawing(CharacterDrawing):
    direction: Direction = Direction.DOWN

    @cached_property
    def coordinate(self) -> Coordinate:
        return Coordinate(0, 0)

    @cached_property
    def drawing(self) -> Drawing:
        return Drawing(MockSurface("a"))

    def turn(self, direction: Direction) -> CharacterDrawing:
        return replace(self, direction=direction)

    def tick_move(self, time_delta: Millisecond) -> CharacterDrawing:
        return self

    def tick_idle(self, time_delta: Millisecond) -> CharacterDrawing:
        return self


@contextmanager
def override_config(cfg: Config) -> Generator[Config, None, None]:
    previous_config = config()
    try:
        yield set_config(cfg)
    finally:
        set_config(previous_config)
