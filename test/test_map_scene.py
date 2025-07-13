from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

from pygame import Event, QUIT
from pytest_mock import MockerFixture

from nextrpg.character.character_on_screen import CharacterSpec
from nextrpg.character.npcs import NpcSpec
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.config.config import Config
from nextrpg.config.debug_config import DebugConfig
from nextrpg.config.resource_config import ResourceConfig
from nextrpg.draw.coordinate import Coordinate
from nextrpg.core import Size
from nextrpg.draw.draw_on_screen import DrawOnScreen, Drawing, Rectangle
from nextrpg.event.pygame_event import Quit
from nextrpg.scene.map_helper import TileBottomAndDrawOnScreen
from nextrpg.scene.map_scene import MapScene, Move
from nextrpg.scene.map_util import _shift
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
    helper.collision_visuals = ()
    mocker.patch("nextrpg.scene.map_scene.MapHelper", return_value=helper)
    map = MapScene(
        tmx_file=Path("test"),
        player_spec=CharacterSpec(
            character=MockCharacterDrawing(), object_name=""
        ),
    )
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
    assert map.event(Quit(Event(QUIT)))


def test_init_npc(mocker: MockerFixture) -> None:
    map_helper = Mock()
    map_helper.get_object.return_value = SimpleNamespace(
        x=1, y=2, width=1, height=1, points=(SimpleNamespace(x=1, y=2),)
    )
    map_helper.collisions = ()
    map_helper.collision_visuals = ()
    mocker.patch("nextrpg.scene.map_scene.MapHelper", map_helper)
    mocker.patch("nextrpg.scene.map_scene.get_polygon")
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
    mocker.patch("nextrpg.scene.map_scene.MapHelper", map_helper)
    mocker.patch("nextrpg.scene.map_scene.get_polygon", return_value=None)
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
    assert _shift(1, 2, 3) == 0
    assert _shift(12, 3, 2) == 1
    assert _shift(12, 10, 100) == -7
    assert _shift(0, 10, 10) == 0
