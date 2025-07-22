from functools import cached_property
from typing import Self, override

from pygame import Event
from pygame.locals import QUIT

from test.util import MockSurface, MockScene
from nextrpg import (
    Coordinate,
    Drawing,
    DrawOnScreen,
    Millisecond,
    PygameEvent,
    Scene,
)


def test_scene() -> None:
    scene = MockScene()
    assert scene.event(PygameEvent(Event(QUIT))) is scene
    assert scene.tick(10) is scene
    assert not scene.draw_on_screens_before_shift

    class MyScene(Scene):
        @override
        @cached_property
        def draw_on_screen_shift(self) -> Coordinate:
            return Coordinate(1, 2)

        @override
        def tick(self, time_delta: Millisecond) -> Scene:
            return self

    assert MyScene().tick(0)
    assert not MyScene().draw_on_screens

    class MyScene(Scene):
        @override
        @cached_property
        def draw_on_screen_shift(self) -> Coordinate | None:
            return None

        @override
        @cached_property
        def draw_on_screens_before_shift(self) -> tuple[DrawOnScreen, ...]:
            return (DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface())),)

        @override
        def tick(self, time_delta: Millisecond) -> Self:
            return self

    assert MyScene().draw_on_screens
    assert MyScene().tick(0)
