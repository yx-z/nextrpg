from pygame.event import Event
from pygame.locals import KEYDOWN, KEYUP, K_RIGHT, K_SPACE, QUIT

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.config import Config, DebugConfig
from nextrpg.core import Size
from nextrpg.draw_on_screen import Coordinate, Rectangle
from nextrpg.event.pygame_event import KeyPressDown, KeyPressUp, Quit
from test.util import MockCharacterDrawing, override_config


def test_character_on_screen():
    character = CharacterOnScreen(
        MockCharacterDrawing(),
        Coordinate(10, 20),
        speed=1,
        collisions=[Rectangle(Coordinate(12, 20), Size(1, 1))],
        is_player=True,
    )
    assert character.step(100).coordinate == Coordinate(10, 20)
    assert character.character_and_visuals.character.top_left == Coordinate(
        10, 20
    )
    right = KeyPressDown(Event(KEYDOWN, key=K_RIGHT))
    assert character.event(right).step(1).coordinate == Coordinate(11, 20)
    assert (
        character.event(right)
        .event(KeyPressUp(Event(KEYUP, key=K_RIGHT)))
        ._movement_keys
        == character._movement_keys
    )
    assert character.event(Quit(Event(QUIT)))
    assert (
        character._updated_movement_key(
            KeyPressDown(Event(KEYDOWN, key=K_SPACE))
        )
        == character._movement_keys
    )

    with override_config(Config(debug=DebugConfig(ignore_map_collisions=True))):
        assert character._can_move(Coordinate(100, 100))
        assert CharacterOnScreen(
            MockCharacterDrawing(),
            Coordinate(10, 20),
            speed=1,
            collisions=[Rectangle(Coordinate(12, 20), Size(1, 1))],
            is_player=True
        )._collision_visuals
