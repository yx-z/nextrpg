from pygame.event import Event
from pygame.locals import KEYDOWN, K_RIGHT, QUIT

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.config import Config, DebugConfig
from nextrpg.core import Size
from nextrpg.draw_on_screen import Coordinate, Rectangle
from nextrpg.event.pygame_event import KeyPressDown, Quit
from test.util import MockCharacterDrawing, override_config


def test_character_on_screen():
    character = CharacterOnScreen(
        MockCharacterDrawing(),
        Coordinate(10, 20),
        speed=1,
        collisions=[Rectangle(Coordinate(12, 20), Size(1, 1))],
    )
    assert character.step(100).coordinate == Coordinate(10, 20)
    assert character.character_and_visuals.character.top_left == Coordinate(
        10, 20
    )
    right = KeyPressDown(Event(KEYDOWN, key=K_RIGHT))
    assert character.event(right).step(1).coordinate == Coordinate(11, 20)
    assert character.event(Quit(Event(QUIT)))

    with override_config(Config(debug=DebugConfig(ignore_map_collisions=True))):
        assert character._can_move(123, Coordinate(100, 100))
        assert CharacterOnScreen(
            MockCharacterDrawing(),
            Coordinate(10, 20),
            speed=1,
            collisions=[Rectangle(Coordinate(12, 20), Size(1, 1))],
        )._collision_visuals
