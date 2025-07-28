from dataclasses import dataclass, replace
from functools import cached_property
from types import SimpleNamespace
from typing import Any, NamedTuple, Self, override

from pygame import Surface

from nextrpg import (
    AnimatedOnScreen,
    CharacterDraw,
    CharacterSpec,
    Coordinate,
    Direction,
    Draw,
    DrawOnScreen,
    EventfulScene,
    Millisecond,
    NpcOnScreen,
    NpcSpec,
    PlayerOnScreen,
    PygameEvent,
    Scene,
    Text,
    TextOnScreen,
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
class MockCharacterDraw(CharacterDraw):
    direction: Direction = Direction.DOWN

    @property
    def display_name(self) -> str:
        return "abc"

    @cached_property
    def coordinate(self) -> Coordinate:
        return Coordinate(0, 0)

    @cached_property
    def draw(self) -> Draw:
        return Draw(MockSurface("a"))

    def turn(self, direction: Direction) -> CharacterDraw:
        return replace(self, direction=direction)

    def tick_move(self, time_delta: Millisecond) -> CharacterDraw:
        return self

    def tick_idle(self, time_delta: Millisecond) -> CharacterDraw:
        return self


class MockScene(Scene):
    @override
    def tick(self, time_delta: Millisecond) -> Self:
        return self

    @override
    def event(self, event: PygameEvent) -> Scene:
        return self


class MockEventfulScene(EventfulScene):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    @property
    def npcs(self) -> tuple[NpcOnScreen, ...]:
        return ()

    @property
    def player(self) -> PlayerOnScreen:
        return PlayerOnScreen(
            coordinate=Coordinate(0, 0),
            spec=CharacterSpec(
                object_name="test", character=MockCharacterDraw()
            ),
            collisions=(),
        )


class MockTextOnScreen(TextOnScreen):
    def __init__(self, *args: Any, message: str = "", **kwargs: Any) -> None:
        self.draw_on_screens = (
            DrawOnScreen(Coordinate(0, 0), Draw(MockSurface())),
        )
        self.message = message

    @property
    def top_left(self) -> Coordinate:
        return Coordinate(0, 0)

    @property
    def text(self) -> Text:
        return Text(self.message)


class MockAnimatedOnScreen(AnimatedOnScreen):
    @override
    def tick(self, time_delta: Millisecond) -> Self:
        return self

    @override
    @property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        return (DrawOnScreen(Coordinate(0, 0), Draw(MockSurface())),)


class MockPlayerOnScreen(PlayerOnScreen):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    @property
    def character(self) -> MockCharacterDraw:
        return MockCharacterDraw()

    @property
    def spec(self) -> CharacterSpec:
        return CharacterSpec(object_name="", character=MockCharacterDraw())
