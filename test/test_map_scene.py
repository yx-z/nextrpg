from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

from pygame import Event, QUIT
from pytest_mock import MockerFixture

from nextrpg import (
    CharacterSpec,
    NpcSpec,
    Coordinate,
    Size,
    DrawOnScreen,
    Drawing,
    Rectangle,
    Quit,
    TileBottomAndDrawOnScreen,
    MapScene,
    center_player,
)
from test.util import MockCharacterDrawing, MockSurface


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
        debug_visuals=(),
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
        debug_visuals=(),
    )
    assert map_scene.npcs


def test_shift() -> None:
    assert center_player(1, 2, 3) == 0
    assert center_player(12, 3, 2) == 1
    assert center_player(12, 10, 100) == -7
    assert center_player(0, 10, 10) == 0
