from pygame.event import Event
from pygame.locals import KEYDOWN, KEYUP, K_RIGHT, K_SPACE, QUIT

from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.config import Config, DebugConfig
from nextrpg.core import Size
from nextrpg.draw_on_screen import Rectangle
from nextrpg.coordinate import Coordinate
from nextrpg.event.pygame_event import KeyPressDown, KeyPressUp, Quit
from nextrpg.logger import pop_messages
from test.util import MockCharacterDrawing, override_config


def test_player_on_screen():
    player = PlayerOnScreen(
        character=MockCharacterDrawing(),
        coordinate=Coordinate(10, 20),
        move_speed=0.2,
        collisions=(Rectangle(Coordinate(12, 20), Size(10, 10)),),
    )
    assert player.event(Quit(Event(QUIT))) is player
    assert player.tick(100).coordinate == Coordinate(10, 20)
    assert player.draw_on_screen.top_left == Coordinate(10, 20)
    right = KeyPressDown(Event(KEYDOWN, key=K_RIGHT))
    assert player.event(right).tick(1).coordinate == Coordinate(10, 20)
    assert (
        player.event(right)
        .event(KeyPressUp(Event(KEYUP, key=K_RIGHT)))
        ._movement_keys
        == player._movement_keys
    )
    assert player.event(Quit(Event(QUIT)))
    assert (
        player._updated_movement_key(KeyPressDown(Event(KEYDOWN, key=K_SPACE)))
        == player._movement_keys
    )

    assert player._can_move(Coordinate(10, 20))
    with override_config(Config(debug=DebugConfig())):
        player.event(right).tick(10)
        assert pop_messages(0)

    with override_config(Config(debug=DebugConfig(ignore_map_collisions=True))):
        assert player._can_move(Coordinate(10, 20))
