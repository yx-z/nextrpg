from pygame.event import Event
from pygame.locals import KEYDOWN, K_RIGHT, QUIT

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.common_types import (
    Coordinate,
    Rectangle,
    Size,
)
from nextrpg.event.pygame_event import KeyPressDown, Quit
from test.util import MockCharacterDrawing


def test_character_on_screen():
    character = CharacterOnScreen(
        MockCharacterDrawing(),
        Coordinate(10, 20),
        speed=1,
        collisions=[Rectangle(Coordinate(12, 20), Size(1, 1))],
    )
    assert character.step(100).coordinate == Coordinate(10, 20)
    assert character.draw_on_screen.character.top_left == Coordinate(10, 20)
    right = KeyPressDown(Event(KEYDOWN, {"key": K_RIGHT}))
    assert character.event(right).step(1).coordinate == Coordinate(11, 20)
    assert character.event(Quit(Event(QUIT)))
