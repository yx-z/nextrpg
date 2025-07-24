from pathlib import Path
from test.util import MockSurface

from pygame import Color, Surface
from pygame.locals import SRCALPHA
from pytest_mock import MockerFixture

from nextrpg import (
    Config,
    Coordinate,
    DebugConfig,
    Drawing,
    Rgba,
    Size,
    override_config,
)


def test_drawing(mocker: MockerFixture) -> None:
    surf = MockSurface()
    assert Drawing(surf)._surface

    mocker.patch("nextrpg.draw.drawing.load")
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
