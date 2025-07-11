from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

from pygame import Event, QUIT
from pytest_mock import MockerFixture

from nextrpg.character.character_on_screen import CharacterSpec
from nextrpg.character.npcs import NpcSpec
from nextrpg.config import Config, DebugConfig, ResourceConfig
from nextrpg.draw.coordinate import Coordinate
from nextrpg.core import Size
from nextrpg.draw.draw_on_screen import DrawOnScreen, Drawing, Rectangle
from nextrpg.event.pygame_event import Quit
from nextrpg.scene.map_helper import TileBottomAndDrawOnScreen
from nextrpg.scene.map_scene import MapScene, Move, _shift
from test.util import MockCharacterDrawing, MockSurface, override_config


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
    mocker.patch("nextrpg.scene.map_scene.MapHelper", return_value=helper)
    map = MapScene(
        tmx_file=Path("test"),
        player_spec=CharacterSpec(character=MockCharacterDrawing(), name=""),
    )
    with override_config(Config(debug=DebugConfig())):
        assert MapScene(
            tmx_file=Path("test"),
            player_spec=CharacterSpec(
                character=MockCharacterDrawing(), name=""
            ),
        ).collision_visuals
    mocker.patch(
        "nextrpg.scene.map_scene.sorted",
        return_value=[
            (
                None,
                None,
                DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface())),
            )
        ],
    )
    assert map.draw_on_screens_before_shift
    assert not map.tick(0)._collision_visuals
    assert map.event(Quit(Event(QUIT)))


def test_init_npc(mocker: MockerFixture) -> None:
    map_helper = Mock()
    map_helper.get_object.return_value = SimpleNamespace(
        x=1, y=2, width=1, height=1, points=(SimpleNamespace(x=1, y=2),)
    )
    map_helper.collisions = ()
    mocker.patch("nextrpg.scene.map_scene.MapHelper", map_helper)
    mocker.patch("nextrpg.scene.map_scene.get_polygon")
    map_scene = MapScene(
        tmx_file="",
        player_spec=CharacterSpec(character=MockCharacterDrawing(), name=""),
        npc_specs=(
            NpcSpec(
                name="", character=MockCharacterDrawing(), event=lambda *_: None
            ),
            NpcSpec(
                name="", character=MockCharacterDrawing(), event=lambda *_: None
            ),
        ),
    )
    assert map_scene.npcs


def test_init_moving_npc(mocker: MockerFixture) -> None:
    map_helper = Mock()
    map_helper.get_object.return_value = SimpleNamespace(
        x=1, y=2, width=0, height=0
    )
    map_helper.collisions = ()
    mocker.patch("nextrpg.scene.map_scene.MapHelper", map_helper)
    mocker.patch("nextrpg.scene.map_scene.get_polygon", return_value=None)
    map_scene = MapScene(
        tmx_file="",
        player_spec=CharacterSpec(character=MockCharacterDrawing(), name=""),
        npc_specs=(
            NpcSpec(
                name="", character=MockCharacterDrawing(), event=lambda *_: None
            ),
        ),
    )
    assert map_scene.npcs


def test_move_to_scene(mocker: MockerFixture) -> None:
    helper = MagicMock()
    helper.background = ()
    helper.foreground = (
        (
            TileBottomAndDrawOnScreen(
                10, DrawOnScreen(Coordinate(1, 2), Drawing(MockSurface()))
            ),
        ),
    )
    helper.above_character = ()
    helper.map_size = (100, 200)
    helper.get_object = lambda name: (
        SimpleNamespace(x=0, y=0, width=1, height=2, properties={})
        if name
        else SimpleNamespace(x=10, y=20, width=10, height=20, properties={})
    )
    mocker.patch("nextrpg.scene.map_scene.MapHelper", return_value=helper)
    map = MapScene(
        tmx_file=Path("test"),
        player_spec=CharacterSpec(name="", character=MockCharacterDrawing()),
        moves=(
            Move("to", "from", lambda _: map),
            Move("", "", lambda _: map),
        ),
    )
    assert map._move_to_scene


def test_shift() -> None:
    assert _shift(1, 2, 3) == 0
    assert _shift(12, 3, 2) == 1
    assert _shift(12, 10, 100) == -7
    assert _shift(0, 10, 10) == 0


def test_move(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.scene.map_helper.load_pygame")
    mocker.patch("nextrpg.scene.map_helper.MapHelper.get_object")
    scene = MapScene(
        tmx_file="tmx",
        player_spec=CharacterSpec(name="", character=MockCharacterDrawing()),
    )
    move = Move("", "", lambda _: scene)
    assert move.to_scene(scene, MockCharacterDrawing())

    with override_config(Config(resource=ResourceConfig(map_cache_size=0))):
        assert move.to_scene(scene, MockCharacterDrawing())
