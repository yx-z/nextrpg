from pathlib import Path
from unittest.mock import Mock

from pygame import Color, SRCALPHA, Surface
from pytest_mock import MockerFixture

from nextrpg.common_types import Coordinate, Rectangle, Rgba, Size
from nextrpg.config import Config, DebugConfig
from nextrpg.draw_on_screen import DrawOnScreen, Drawing
from test.util import override_config


def test_drawing(mocker: MockerFixture) -> None:
    surf = Mock()
    mocker.patch("nextrpg.draw_on_screen.load", surf)
    assert Drawing.load(Path("abc"))
    drawing = Drawing(Surface((1, 2), SRCALPHA))
    assert drawing.width == 1
    assert drawing.height == 2
    assert drawing.size == Size(1, 2)
    assert drawing.crop(Size(1, 2), Coordinate(0, 0)).size == Size(1, 2)
    assert (drawing * 10).size == Size(10, 20)
    assert isinstance(drawing.pygame, Surface)

    with override_config(
        Config(debug=DebugConfig(drawing_background_color=Rgba(0, 0, 255, 32)))
    ):
        surface = Drawing(Surface((1, 2), SRCALPHA)).pygame
        assert isinstance(surface, Surface)
        assert surface.get_at((0, 0)) == Color(0, 0, 255, 32)


def test_draw_on_screen() -> None:
    draw_on_screen = DrawOnScreen(Coordinate(10, 20), Drawing(Surface((1, 2))))
    assert draw_on_screen.rectangle == Rectangle(Coordinate(10, 20), Size(1, 2))
    assert draw_on_screen.visible_rectangle == Rectangle(
        Coordinate(10, 20), Size(0, 1)
    )
    surface, coord = draw_on_screen.pygame
    assert isinstance(surface, Surface)
    assert coord == (10, 20)
    scaled = draw_on_screen * 2
    assert scaled.drawing.size == Size(2, 4)
    assert scaled.top_left == Coordinate(20, 40)

    assert DrawOnScreen.from_rectangle(
        Rectangle(Coordinate(0, 0), Size(1, 2)), Rgba(0, 0, 0, 0)
    ).top_left == Coordinate(0, 0)

    assert DrawOnScreen.from_rectangle(
        Rectangle(Coordinate(0, 0), Size(0, 0)), Rgba(0, 0, 0, 0)
    ).visible_rectangle.size == Size(0, 0)
