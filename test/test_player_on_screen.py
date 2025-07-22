from test.util import MockCharacterDrawing

from pygame.event import Event
from pygame.locals import K_RIGHT, K_SPACE, KEYDOWN, KEYUP, QUIT

from nextrpg import (
    CharacterSpec,
    Config,
    Coordinate,
    DebugConfig,
    KeyPressDown,
    KeyPressUp,
    PlayerOnScreen,
    Quit,
    Rectangle,
    Size,
    override_config,
    pop_messages,
)


def test_player_on_screen():
    player = PlayerOnScreen(
        spec=CharacterSpec(object_name="", character=MockCharacterDrawing()),
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

    assert player.stop_move
    assert player.start_move
