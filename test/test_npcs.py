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
    Npcs,
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
            "name",
            MockCharacterDrawing(),
            lambda *_: None,
        ),
    ).tick(0)
    assert npc
    assert (
        npc._trigger(
            PlayerOnScreen(
                collisions=[],
                character=MockCharacterDrawing(),
                coordinate=Coordinate(0, 0),
            )
        ).character.direction
        is Direction.UP
    )


def test_moving_npc_on_screen() -> None:
    npc = MovingNpcOnScreen(
        coordinate=Coordinate(0, 0),
        spec=MovingNpcSpec(
            "name",
            MockCharacterDrawing(),
            lambda *_: None,
            idle_duration=10,
            move_duration=10,
        ),
        path=Rectangle(Coordinate(0, 0), Size(10, 10)),
        collisions=[],
    )
    assert not npc.tick(0).is_moving
    assert not npc.tick(5).tick(1).is_moving
    assert npc.tick(11).tick(9).is_moving
    assert not npc.tick(11).tick(20).is_moving
    assert npc.move(0) == Coordinate(0, 0)


def test_npcs(mocker: MockerFixture) -> None:
    def event(p: PlayerOnScreen, *args: Any) -> None:
        res = say(p, "hi")
        assert res
        say(p, "hi")

    npcs = Npcs(
        list=[
            NpcOnScreen(
                coordinate=Coordinate(0, 0),
                spec=NpcSpec("name", MockCharacterDrawing(), event),
            ),
            MovingNpcOnScreen(
                coordinate=Coordinate(0, 0),
                spec=MovingNpcSpec(
                    "name",
                    MockCharacterDrawing(),
                    event,
                ),
                collisions=[],
                path=Rectangle(Coordinate(0, 0), Size(10, 10)),
            ),
        ],
    )
    assert npcs.tick(1)
    assert not npcs.event(
        KeyPressDown(Event(KEYDOWN, key=K_RETURN)),
        PlayerOnScreen(
            character=MockCharacterDrawing(),
            coordinate=Coordinate(100, 100),
            collisions=[],
        ),
        EventfulScene(npcs),
    )

    map_helper = Mock()
    map_helper.get_object.return_value = SimpleNamespace(
        x=1, y=1, width=1, height=1
    )
    map_helper.foreground = []
    map_helper.background = []
    map_helper.above_character = []
    map_helper.map_size = Size(100, 100)
    mocker.patch("nextrpg.scene.map_scene.MapHelper", return_value=map_helper)
    mocker.patch("nextrpg.scene.map_scene.merge", return_value=[])
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
    object.__setattr__(map_scene, "draw_on_screens", [])
    say_event = npcs.event(
        KeyPressDown(Event(KEYDOWN, key=K_RETURN)), player, map_scene
    )
    assert say_event.tick(0)
    assert say_event.draw_on_screens
    assert say_event.event(Quit(Event(QUIT)))
    assert say_event.event(KeyPressDown(Event(KEYDOWN, key=K_SPACE)))
    new_scene = say_event.event(KeyPressDown(Event(KEYDOWN, key=K_RETURN)))
    assert isinstance(new_scene, MapScene)


def test_eventful_scene() -> None:
    def event() -> RpgEventGenerator:
        yield lambda generator, scene: RpgEventScene(generator, scene)

    gen = event()
    eventful = EventfulScene(
        Npcs(
            list=[
                NpcOnScreen(
                    coordinate=Coordinate(0, 0),
                    spec=NpcSpec(
                        "npc", MockCharacterDrawing(), lambda *_: None
                    ),
                )
            ]
        ),
        _event=gen,
        _npc=NpcOnScreen(
            coordinate=Coordinate(0, 0),
            spec=NpcSpec(
                "npc",
                MockCharacterDrawing(),
                lambda *_: None,
            ),
        ),
    )
    assert eventful.tick_without_event(0)
    next(gen)
    assert eventful._next_event
