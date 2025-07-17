from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, Mock

from pygame import Event, QUIT
from pytest_mock import MockerFixture

from nextrpg import (
    CharacterSpec,
    Config,
    Coordinate,
    DebugConfig,
    DrawOnScreen,
    Drawing,
    MapScene,
    Move,
    NpcSpec,
    Quit,
    Rectangle,
    ResourceConfig,
    Size,
    TileBottomAndDrawOnScreen,
)
from test.util import MockCharacterDrawing, MockSurface
from test.util import override_config


def test_map_scene(mocker: MockerFixture) -> None:
    helper = MagicMock()
    helper.background = ()
    foreground = TileBottomAndDrawOnScreen(
        10, DrawOnScreen(Coordinate(1, 2), Drawing(MockSurface()))
    )
    helper.foreground = ((foreground,),)
    helper.above_character = ()
    helper.map_size = (100, 200)
    helper.get_object.return_value = SimpleNamespace(
        x=0, y=0, width=1, height=2, properties={}
    )
    helper.collisions = (Rectangle(Coordinate(0, 0), Size(0, 0)),)
    helper.collision_visuals = ()
    mocker.patch("nextrpg.map_scene.MapHelper", return_value=helper)
    map = MapScene(
        tmx_file=Path("test"),
        player_spec=CharacterSpec(
            character=MockCharacterDrawing(), object_name=""
        ),
    )
    mocker.patch(
        "nextrpg.map_scene.sorted",
        return_value=[
            (
                None,
                None,
                DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface())),
            )
        ],
    )
    assert map.draw_on_screens_before_shift
    assert map.event(Quit(Event(QUIT)))
    assert map.tick(0)
    assert map.tick_without_transition(0)
    assert map.tick_without_event(0)


def test_move(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.map_scene.MapHelper")
    mocker.patch("nextrpg.map_scene.MapHelper.get_object")
    mocker.patch("nextrpg.map_scene.get_polygon")
    i = 0

    def _increment(*_: Any) -> bool:
        nonlocal i
        i += 1
        return i % 2 == 0

    mocker.patch("nextrpg.draw.draw_on_screen.Rectangle.collide", _increment)

    def to_scene(*_: Any) -> MapScene:
        return MapScene(
            tmx_file="test2",
            player_spec=CharacterSpec(
                character=MockCharacterDrawing(), object_name=""
            ),
        )

    map = MapScene(
        tmx_file="test2",
        player_spec=CharacterSpec(
            character=MockCharacterDrawing(), object_name=""
        ),
        moves=(Move("from", "to", to_scene), Move("from2", "to2", to_scene)),
    )
    assert map._move_to_scene
    assert MapScene(
        tmx_file="test2",
        player_spec=CharacterSpec(
            character=MockCharacterDrawing(), object_name=""
        ),
        moves=(
            Move("from", "test2", to_scene),
            Move("from2", "test2", to_scene),
        ),
    )._move_to_scene

    with override_config(Config(resource=ResourceConfig(map_cache_size=1))):
        assert MapScene(
            tmx_file="test2",
            player_spec=CharacterSpec(
                character=MockCharacterDrawing(), object_name=""
            ),
            moves=(
                Move("from", "test2", to_scene),
                Move("from2", "test2", to_scene),
            ),
        )._move_to_scene


def test_init_npc(mocker: MockerFixture) -> None:
    map_helper = Mock()
    map_helper.get_object.return_value = SimpleNamespace(
        x=1, y=2, width=1, height=1, points=(SimpleNamespace(x=1, y=2),)
    )
    map_helper.collisions = ()
    map_helper.collision_visuals = ()
    mocker.patch("nextrpg.map_scene.MapHelper", map_helper)
    mocker.patch("nextrpg.map_scene.get_polygon")
    map_scene = MapScene(
        tmx_file="",
        player_spec=CharacterSpec(
            character=MockCharacterDrawing(), object_name=""
        ),
        npc_specs=(
            NpcSpec(
                object_name="",
                character=MockCharacterDrawing(),
                event=lambda *_: None,
            ),
            NpcSpec(
                object_name="",
                character=MockCharacterDrawing(),
                event=lambda *_: None,
            ),
        ),
        _debug_visuals=(),
    )
    assert map_scene.npcs


def test_init_moving_npc(mocker: MockerFixture) -> None:
    map_helper = Mock()
    map_helper.get_object.return_value = SimpleNamespace(
        x=1, y=2, width=0, height=0
    )
    map_helper.collisions = ()
    map_helper.collision_visuals = ()
    mocker.patch("nextrpg.map_scene.MapHelper", map_helper)
    mocker.patch("nextrpg.map_scene.get_polygon", return_value=None)
    map_scene = MapScene(
        tmx_file="",
        player_spec=CharacterSpec(
            character=MockCharacterDrawing(), object_name=""
        ),
        npc_specs=(
            NpcSpec(
                object_name="",
                character=MockCharacterDrawing(),
                event=lambda *_: None,
            ),
        ),
        _debug_visuals=(),
    )
    assert map_scene.npcs

    with override_config(Config(debug=DebugConfig())):
        assert not map_scene._npc_paths
