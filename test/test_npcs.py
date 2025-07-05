from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock

from pygame import Event, K_SPACE
from pygame.locals import KEYDOWN, K_RETURN, QUIT
from pytest_mock import MockerFixture

from nextrpg.character.npcs import (
    MovingNpcOnScreen,
    MovingNpcSpec,
    NpcOnScreen,
    NpcSpec,
    Npcs,
)
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.core import Size
from nextrpg.draw_on_screen import Coordinate, Rectangle
from nextrpg.event.pygame_event import KeyPressDown, Quit
from nextrpg.event.say import say
from nextrpg.scene.map_scene import MapScene
from nextrpg.scene.scene import Scene
from test.util import MockCharacterDrawing


def test_npc_on_screen() -> None:
    assert NpcOnScreen(
        coordinate=Coordinate(0, 0),
        character=MockCharacterDrawing(),
        name="name",
        event_spec=lambda *_: None,
    ).tick(0)


def test_moving_npc_on_screen() -> None:
    npc = MovingNpcOnScreen(
        coordinate=Coordinate(0, 0),
        character=MockCharacterDrawing(),
        name="name",
        event_spec=lambda *_: None,
        move_speed=0.2,
        path=Rectangle(Coordinate(0, 0), Size(10, 10)),
        idle_duration=10,
        move_duration=10,
        collisions=[],
    )
    assert not npc.tick(0).is_moving
    assert not npc.tick(5).tick(1).is_moving
    assert npc.tick(11).tick(9).is_moving
    assert not npc.tick(11).tick(20).is_moving
    assert npc.move(0) == Coordinate(0, 0)


def test_npcs(mocker: MockerFixture) -> None:
    map_helper = Mock()
    map_helper.get_object.return_value = SimpleNamespace(
        x=1, y=1, width=1, height=1
    )
    map_helper.map_size = Size(100, 100)

    def event(player: PlayerOnScreen, *args: Any) -> None:
        say(player, "hi")

    npcs = Npcs(
        map_helper=map_helper,
        specs=[
            NpcSpec(
                name="name",
                event_spec=event,
                drawing=MockCharacterDrawing(),
            ),
            MovingNpcSpec(
                name="name",
                event_spec=event,
                drawing=MockCharacterDrawing(),
                observe_collisions=False,
            ),
        ],
    )
    assert npcs.tick(1)
    assert not npcs.trigger(
        PlayerOnScreen(
            character=MockCharacterDrawing(),
            coordinate=Coordinate(100, 100),
            collisions=[],
        ),
        Scene(),
    )

    mocker.patch("nextrpg.scene.map_scene.MapHelper", return_value=map_helper)
    player = PlayerOnScreen(
        character=MockCharacterDrawing(),
        coordinate=Coordinate(0, 0),
        collisions=[],
    )
    assert not event(player)
    map_scene = MapScene(
        tmx_file="",
        initial_player_drawing=MockCharacterDrawing(),
        player_coordinate_object="",
    )
    map_scene.draw_on_screens = []
    say_event = npcs.trigger(player, map_scene)
    assert say_event
    assert say_event.draw_on_screens
    assert say_event.event(Quit(Event(QUIT)))
    assert say_event.event(KeyPressDown(Event(KEYDOWN, key=K_SPACE)))
    new_scene = say_event.event(KeyPressDown(Event(KEYDOWN, key=K_RETURN)))
    assert isinstance(new_scene, MapScene)
