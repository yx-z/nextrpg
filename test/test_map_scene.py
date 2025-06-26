from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from pygame import Event, QUIT
from pytest_mock import MockerFixture

from nextrpg.draw_on_screen import Coordinate, DrawOnScreen, Drawing
from nextrpg.event.pygame_event import Quit
from nextrpg.scene.map_helper import TileBottomAndDraw
from nextrpg.scene.map_scene import MapScene, _offset
from test.util import MockCharacterDrawing, MockSurface


def test_map_scene(mocker: MockerFixture) -> None:
    helper = MagicMock()
    helper.background = []
    helper.foreground = [
        {
            TileBottomAndDraw(
                10, DrawOnScreen(Coordinate(1, 2), Drawing(MockSurface()))
            )
        }
    ]
    helper.above_character = []
    helper.map_size.tuple = (100, 200)
    helper.get_object.return_value = SimpleNamespace(x=10, y=20, properties={})
    mocker.patch("nextrpg.scene.map_scene.MapHelper", return_value=helper)
    map = MapScene(Path("test"), MockCharacterDrawing())
    assert map.event(Quit(Event(QUIT)))
    assert map.step(1).draw_on_screens


def test_offset() -> None:
    assert _offset(1, 2, 3) == 0
    assert _offset(12, 3, 2) == 1
    assert _offset(12, 10, 100) == -7
