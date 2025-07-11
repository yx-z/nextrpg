from pygame import Event
from pygame.locals import QUIT

from nextrpg.draw.coordinate import Coordinate
from nextrpg.draw.draw_on_screen import DrawOnScreen, Drawing
from nextrpg.event.pygame_event import PygameEvent
from nextrpg.scene.scene import Scene
from test.util import MockSurface


def test_scene() -> None:
    scene = Scene()
    assert scene.event(PygameEvent(Event(QUIT))) is scene
    assert scene.tick(10) is scene
    assert not scene.draw_on_screens_before_shift

    scene.draw_on_screen_shift = Coordinate(1, 2)
    scene.draw_on_screens_before_shift = (
        DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface())),
    )
    assert scene.draw_on_screens
