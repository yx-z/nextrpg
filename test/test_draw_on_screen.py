from pathlib import Path
from unittest.mock import Mock

from pygame import Color, SRCALPHA, Surface
from pytest_mock import MockerFixture

from nextrpg.config import Config, DebugConfig
from nextrpg.core import Coordinate, Rgba, Size
from nextrpg.draw_on_screen import DrawOnScreen, Drawing, Rectangle
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
    assert isinstance(drawing.pygame, Surface)

    with override_config(
        Config(debug=DebugConfig(drawing_background_color=Rgba(0, 0, 255, 32)))
    ):
        surface = Drawing(Surface((1, 2), SRCALPHA)).pygame
        assert isinstance(surface, Surface)
        assert surface.get_at((0, 0)) == Color(0, 0, 255, 32)


def test_rectangle() -> None:
    rect = Rectangle(Coordinate(10, 20), Size(2, 2))
    assert rect.size == Size(2, 2)
    assert rect.left == 10
    assert rect.top == 20
    assert rect.right == 12
    assert rect.bottom == 22
    assert rect.top_left == Coordinate(10, 20)
    assert rect.top_right == Coordinate(12, 20)
    assert rect.bottom_left == Coordinate(10, 22)
    assert rect.bottom_right == Coordinate(12, 22)
    assert rect.top_center == Coordinate(11, 20)
    assert rect.bottom_center == Coordinate(11, 22)
    assert rect.center_left == Coordinate(10, 21)
    assert rect.center_right == Coordinate(12, 21)
    assert rect.center == Coordinate(11, 21)
    assert rect.collide(Rectangle(Coordinate(9, 20), Size(10, 20)))
    assert Coordinate(11, 21) in rect


def test_draw_on_screen() -> None:
    draw_on_screen = DrawOnScreen(Coordinate(10, 20), Drawing(Surface((1, 2))))
    assert draw_on_screen.rectangle == Rectangle(Coordinate(10, 20), Size(1, 2))
    assert draw_on_screen.visible_rectangle == Rectangle(
        Coordinate(10, 20), Size(0, 1)
    )
    surface, coord = draw_on_screen.pygame
    assert isinstance(surface, Surface)
    assert coord == (10, 20)

    assert DrawOnScreen.from_rectangle(
        Rectangle(Coordinate(0, 0), Size(1, 2)), Rgba(0, 0, 0, 0)
    ).top_left == Coordinate(0, 0)

    assert DrawOnScreen.from_rectangle(
        Rectangle(Coordinate(0, 0), Size(0, 0)), Rgba(0, 0, 0, 0)
    ).visible_rectangle.size == Size(0, 0)
