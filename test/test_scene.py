from pygame import Event
from pygame.locals import QUIT

from nextrpg.event.pygame_event import PygameEvent
from nextrpg.scene.scene import Scene


def test_scene() -> None:
    scene = Scene()
    assert scene.event(PygameEvent(Event(QUIT))) is scene
    assert scene.tick(10) is scene
    assert not scene._draw_on_screens
