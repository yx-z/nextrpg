from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from pygame import Event, QUIT
from pytest_mock import MockerFixture

from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.config import Config, DebugConfig
from nextrpg.core import Size
from nextrpg.draw_on_screen import Coordinate, DrawOnScreen, Drawing, Rectangle
from nextrpg.event.move import Move
from nextrpg.event.pygame_event import Quit
from nextrpg.scene.map_helper import TileBottomAndDrawOnScreen
from nextrpg.scene.map_scene import MapScene, _shift
from nextrpg.scene.scene import Scene
from test.util import MockCharacterDrawing, MockSurface, override_config


def test_map_scene(mocker: MockerFixture) -> None:
    helper = MagicMock()
    helper.background = []
    foreground = TileBottomAndDrawOnScreen(
        10, DrawOnScreen(Coordinate(1, 2), Drawing(MockSurface()))
    )
    helper.foreground = [[foreground]]
    helper.above_character = []
    helper.map_size = (100, 200)
    helper.get_object.return_value = SimpleNamespace(
        x=0, y=0, width=1, height=2, properties={}
    )
    helper.collisions = [Rectangle(Coordinate(0, 0), Size(0, 0))]
    mocker.patch("nextrpg.scene.map_scene.MapHelper", return_value=helper)
    map = MapScene(
        tmx_file=Path("test"),
        initial_player_drawing=MockCharacterDrawing(),
        player_coordinate_object="",
    )
    with override_config(Config(debug=DebugConfig())):
        assert map._collision_visuals
    mocker.patch(
        "nextrpg.scene.map_scene.merge",
        return_value=[
            (None, None, DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface())))
        ],
    )
    assert map.draw_on_screens
    assert not map.tick(0)._collision_visuals
    assert map.event(Quit(Event(QUIT)))


def test_move_to_scene(mocker: MockerFixture) -> None:
    helper = MagicMock()
    helper.background = []
    helper.foreground = [
        [
            TileBottomAndDrawOnScreen(
                10, DrawOnScreen(Coordinate(1, 2), Drawing(MockSurface()))
            )
        ]
    ]
    helper.above_character = []
    helper.map_size = (100, 200)
    helper.get_object = lambda name: (
        SimpleNamespace(x=0, y=0, width=1, height=2, properties={})
        if name
        else SimpleNamespace(x=10, y=20, width=10, height=20, properties={})
    )
    mocker.patch("nextrpg.scene.map_scene.MapHelper", return_value=helper)
    map = MapScene(
        tmx_file=Path("test"),
        initial_player_drawing=MockCharacterDrawing(),
        player_coordinate_object="",
        moves=[
            Move("to", "from", lambda _, __: Scene()),
            Move("", "", lambda _, __: Scene()),
        ],
    )
    assert map._move_to_scene(
        PlayerOnScreen(
            character=MockCharacterDrawing(),
            coordinate=Coordinate(11, 21),
            collisions=[],
        )
    )


def test_shift() -> None:
    assert _shift(1, 2, 3) == 0
    assert _shift(12, 3, 2) == 1
    assert _shift(12, 10, 100) == -7
    assert _shift(0, 10, 10) == 0
