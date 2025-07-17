from functools import cached_property
from test.util import MockSurface

from pygame import Event
from pygame.locals import QUIT

from nextrpg import Coordinate, Drawing, DrawOnScreen, PygameEvent, Scene


def test_scene() -> None:
    scene = Scene()
    assert scene.event(PygameEvent(Event(QUIT))) is scene
    assert scene.tick(10) is scene
    assert not scene.draw_on_screens_before_shift

    class MyScene(Scene):
        @cached_property
        def draw_on_screen_shift(self) -> Coordinate:
            return Coordinate(1, 2)

    assert not MyScene().draw_on_screens

    class MyScene(Scene):
        @cached_property
        def draw_on_screen_shift(self) -> Coordinate | None:
            return None

        @cached_property
        def draw_on_screens_before_shift(self) -> tuple[DrawOnScreen, ...]:
            return (DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface())),)

    assert MyScene().draw_on_screens
