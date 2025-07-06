from pathlib import Path

from pygame import Color, SRCALPHA, Surface
from pytest_mock import MockerFixture

from nextrpg.config import Config, DebugConfig
from nextrpg.coordinate import Coordinate
from nextrpg.core import Rgba, Size
from nextrpg.drawing import Drawing
from test.util import MockSurface, override_config


def test_drawing(mocker: MockerFixture) -> None:
    surf = MockSurface()
    assert Drawing(surf)._surface

    mocker.patch("nextrpg.drawing.load")
    assert Drawing(Path("abc"))._surface
    drawing = Drawing(Surface((1, 2), SRCALPHA))
    assert drawing.width == 1
    assert drawing.height == 2
    assert drawing.size == Size(1, 2)
    assert drawing.crop(Coordinate(0, 0), Size(1, 2)).size == Size(1, 2)
    assert isinstance(drawing.pygame, Surface)

    assert drawing.set_alpha(0) is not drawing

    with override_config(
        Config(debug=DebugConfig(drawing_background_color=Rgba(0, 0, 255, 32)))
    ):
        surface = Drawing(Surface((1, 2), SRCALPHA)).pygame
        assert isinstance(surface, Surface)
        assert surface.get_at((0, 0)) == Color(0, 0, 255, 32)
