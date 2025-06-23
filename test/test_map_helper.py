from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from nextrpg.core import Size
from nextrpg.scene.map_helper import MapHelper
from test.util import MockSurface


def test_map_helper(mocker: MockerFixture) -> None:
    mock_tmx = MagicMock()
    mock_tmx.width = 10
    mock_tmx.height = 20
    mock_tmx.tilewidth = 2
    mock_tmx.tileheight = 3
    mock_background = MagicMock()
    mock_background.name = "background"
    mock_background.tiles = lambda: [(1, 2, MockSurface())]
    mock_foreground = MagicMock()
    mock_foreground.name = "foreground"
    mock_foreground.tiles = lambda: [
        (0, 0, MockSurface()),
        (1, 1, MockSurface()),
    ]
    mock_foreground.data = [[1, 0], [0, 0]]
    mock_above_character = MagicMock()
    mock_above_character.name = "above_character"
    mock_above_character.tiles = lambda: [(5, 6, MockSurface())]
    mock_object = MagicMock()
    mock_object.name = "object"
    mock_object.__iter__.return_value = iter([SimpleNamespace(name="obj")])
    mock_tmx.layers = [
        mock_background,
        mock_foreground,
        mock_above_character,
        mock_object,
    ]
    mock_tmx.tile_properties = {
        1: {"id": 1, "type": "abc"},
        2: {"id": 2, "type": "abc"},
        3: {"id": 3, "type": "def"},
    }
    mocker.patch("nextrpg.scene.map_helper.load_pygame", return_value=mock_tmx)
    helper = MapHelper(Path())
    assert helper.map_size == Size(20, 60)
    assert helper.background
    assert helper.above_character
    assert helper.foreground
    assert helper.get_object("obj")
