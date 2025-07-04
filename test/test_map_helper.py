from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.config import Config, ResourceConfig
from nextrpg.core import Size
from nextrpg.draw_on_screen import Coordinate
from nextrpg.scene.map_helper import MapHelper
from test.util import MockCharacterDrawing, MockSurface, override_config


@override_config(Config(resource=ResourceConfig(map_cache_size=1)))
def test_map_helper(mocker: MockerFixture) -> None:
    tmx = MagicMock()
    tmx.width = 10
    tmx.height = 20
    tmx.tilewidth = 2
    tmx.tileheight = 3
    mock_background = MagicMock()
    setattr(mock_background, "class", "background")
    mock_background.tiles = lambda: [(1, 2, MockSurface())]
    mock_foreground = MagicMock()
    setattr(mock_foreground, "class", "foreground")
    mock_foreground.__iter__.return_value = iter(
        [(1, 2, 4), (2, 3, 5), (3, 4, 6)]
    )
    mock_foreground.tiles = lambda: [
        (0, 0, MockSurface()),
        (1, 1, MockSurface()),
    ]
    mock_foreground.data = [[1, 0], [0, 0]]
    mock_above_character = MagicMock()
    setattr(mock_above_character, "class", "above_character")
    mock_above_character.tiles = lambda: [(5, 6, MockSurface())]
    mock_object = MagicMock()
    obj = SimpleNamespace(
        name="obj",
        type="collision",
        width=None,
        as_points=[(1, 2), (3, 4), (5, 6)],
    )
    mock_object.__iter__.return_value = iter([obj])
    tmx.visible_tile_layers = [0, 1, 2]
    tmx.layers = [
        mock_background,
        mock_foreground,
        mock_above_character,
        mock_object,
    ]
    tmx.visible_object_groups = [3]
    tmx.tile_properties = {
        1: {"id": 1, "type": "abc"},
        2: {"id": 2, "type": "abc"},
        3: {"id": 3, "type": "def"},
        4: {
            "colliders": [
                SimpleNamespace(
                    as_points=[(1, 2), (3, 4), (5, 6)], x=None, width=None
                )
            ]
        },
        5: {
            "colliders": [
                SimpleNamespace(as_points=[], x=1, y=2, width=3, height=4)
            ]
        },
    }
    mocker.patch("nextrpg.scene.map_helper.load_pygame", return_value=tmx)
    helper = MapHelper(Path("abc"))
    assert helper.map_size == Size(20, 60)
    assert helper.background
    assert helper.above_character
    assert helper.foreground
    assert helper.get_object("obj")
    assert helper.collisions
    assert helper.layer_bottom_and_draw(
        PlayerOnScreen(
            coordinate=Coordinate(0, 0),
            character=MockCharacterDrawing(),
            collisions=[],
        )
    )
    assert MapHelper(Path("abc")) is helper
    assert MapHelper(Path("def")) is not helper
