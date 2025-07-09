from dataclasses import replace
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock

from pygame import Event, K_SPACE
from pygame.locals import KEYDOWN, K_RETURN, QUIT
from pytest_mock import MockerFixture

from nextrpg.character.moving_npc import MovingNpcOnScreen, MovingNpcSpec
from nextrpg.character.npcs import (
    EventfulScene,
    NpcOnScreen,
    NpcSpec,
    RpgEventGenerator,
    RpgEventScene,
)
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.core import Direction, Size
from nextrpg.draw_on_screen import Rectangle
from nextrpg.coordinate import Coordinate
from nextrpg.event.pygame_event import KeyPressDown, Quit
from nextrpg.event.say import say
from nextrpg.scene.map_scene import MapScene
from test.util import MockCharacterDrawing


def test_npc_on_screen() -> None:
    npc = NpcOnScreen(
        coordinate=Coordinate(0, 0),
        spec=NpcSpec(
            name="name",
            character=MockCharacterDrawing(),
            event=lambda *_: None,
        ),
    ).tick(0)
    assert npc
    assert (
        npc.start_event(
            PlayerOnScreen(
                collisions=(),
                character=MockCharacterDrawing(),
                coordinate=Coordinate(0, 0),
            )
        ).character.direction
        is Direction.RIGHT
    )


def test_npcs(mocker: MockerFixture) -> None:
    def event(p: PlayerOnScreen, *args: Any) -> None:
        res = say(p, "hi")
        assert res
        say(p, "hi")

    map_helper = Mock()
    map_helper.get_object.return_value = SimpleNamespace(
        x=1, y=1, width=1, height=1
    )
    map_helper.foreground = ()
    map_helper.background = ()
    map_helper.above_character = ()
    map_helper.map_size = Size(100, 100)
    mocker.patch("nextrpg.scene.map_scene.MapHelper", return_value=map_helper)
    mocker.patch(
        "nextrpg.scene.map_scene.MapScene.draw_on_screens_before_shift",
        return_value=(),
    )
    player = PlayerOnScreen(
        character=MockCharacterDrawing(),
        coordinate=Coordinate(0, 0),
        collisions=(),
    )
    assert not event(player)
    map_scene = MapScene(
        tmx_file="",
        initial_player_drawing=MockCharacterDrawing(),
        player_coordinate_object="",
        _npcs=(
            NpcOnScreen(
                coordinate=Coordinate(0, 0),
                spec=NpcSpec(
                    name="name", character=MockCharacterDrawing(), event=event
                ),
            ),
            MovingNpcOnScreen(
                coordinate=Coordinate(0, 0),
                spec=MovingNpcSpec(
                    name="name",
                    character=MockCharacterDrawing(),
                    event=event,
                ),
                collisions=(),
                path=Rectangle(Coordinate(0, 0), Size(10, 10)),
            ),
        ),
    )
    assert map_scene.npcs
    say_event = map_scene.event(KeyPressDown(Event(KEYDOWN, key=K_RETURN)))
    object.__setattr__(say_event._scene, "draw_on_screens", ())
    assert say_event.tick(0)
    assert say_event.draw_on_screens
    assert say_event.event(Quit(Event(QUIT)))
    assert say_event.event(KeyPressDown(Event(KEYDOWN, key=K_SPACE)))
    new_scene = say_event.event(KeyPressDown(Event(KEYDOWN, key=K_RETURN)))
    assert isinstance(new_scene, MapScene)
    player = replace(map_scene._player, coordinate=Coordinate(123, 100))
    assert not replace(map_scene, _player=player)._collided_npc


def test_eventful_scene() -> None:
    def event() -> RpgEventGenerator:
        yield lambda generator, scene: RpgEventScene(generator, scene)

    gen = event()
    eventful = EventfulScene(
        _player=PlayerOnScreen(
            coordinate=Coordinate(0, 0),
            character=MockCharacterDrawing(),
            collisions=(),
        ),
        _npcs=(
            NpcOnScreen(
                coordinate=Coordinate(0, 0),
                spec=NpcSpec(
                    name="npc",
                    character=MockCharacterDrawing(),
                    event=lambda *_: None,
                ),
            ),
        ),
        _event=gen,
        _npc=NpcOnScreen(
            coordinate=Coordinate(0, 0),
            spec=NpcSpec(
                name="npc",
                character=MockCharacterDrawing(),
                event=lambda *_: None,
            ),
        ),
    )
    assert eventful.tick(0)
    assert eventful._next_event

    gen2 = event()
    next(gen2)
    npc = NpcOnScreen(
        name="abc",
        character=MockCharacterDrawing(),
        coordinate=Coordinate(0, 0),
        spec=lambda *_: None,
    )
    scene = EventfulScene(
        _player=PlayerOnScreen(
            coordinate=Coordinate(0, 0),
            character=MockCharacterDrawing(),
            collisions=(),
        ),
        _npc=npc,
        _npcs=(npc,),
        _event=gen2,
    )
    assert scene._next_event
