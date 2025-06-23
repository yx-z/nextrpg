from pathlib import Path
from unittest.mock import Mock

from pygame import Color, SRCALPHA, Surface
from pytest import approx, raises
from pytest_mock import MockerFixture

from nextrpg.config import Config, DebugConfig
from nextrpg.core import Direction, DirectionalOffset, Rgba, Size
from nextrpg.draw_on_screen import (
    Coordinate,
    DrawOnScreen,
    Drawing,
    Polygon,
    Rectangle,
)
from test.util import override_config


def test_drawing(mocker: MockerFixture) -> None:
    surf = Mock()
    mocker.patch("nextrpg.draw_on_screen.load", surf)
    assert Drawing(Path("abc"))
    drawing = Drawing(Surface((1, 2), SRCALPHA))
    assert drawing.width == 1
    assert drawing.height == 2
    assert drawing.size == Size(1, 2)
    assert drawing.crop(Coordinate(0, 0), Size(1, 2)).size == Size(1, 2)
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

    assert Rectangle(Coordinate(0, 0), Size(1, 2)).fill(
        Rgba(0, 0, 0, 0)
    ).top_left == Coordinate(0, 0)

    assert Rectangle(Coordinate(0, 0), Size(0, 0)).fill(
        Rgba(0, 0, 0, 0)
    ).visible_rectangle.size == Size(0, 0)


def test_coordinate() -> None:
    assert Coordinate(10, 20) * 2 == Coordinate(20, 40)
    assert Coordinate(10, 20) + DirectionalOffset(
        Direction.UP, 5
    ) == Coordinate(10, 15)
    assert Coordinate(10, 20) + DirectionalOffset(
        Direction.DOWN, 5
    ) == Coordinate(10, 25)
    assert Coordinate(10, 20) + DirectionalOffset(
        Direction.LEFT, 5
    ) == Coordinate(5, 20)
    assert Coordinate(10, 20) + DirectionalOffset(
        Direction.RIGHT, 5
    ) == Coordinate(15, 20)
    assert Coordinate(10, 20) + DirectionalOffset(
        Direction.UP_LEFT, 10
    ) == approx(Coordinate(2.9289321881345254, 12.928932188134524))
    assert Coordinate(10, 20) + DirectionalOffset(
        Direction.UP_RIGHT, 10
    ) == approx(Coordinate(17.071067811865476, 12.928932188134524))
    assert Coordinate(10, 20) + DirectionalOffset(
        Direction.DOWN_LEFT, 10
    ) == approx(Coordinate(2.9289321881345254, 27.071067811865476))
    assert Coordinate(10, 20) + DirectionalOffset(
        Direction.DOWN_RIGHT, 10
    ) == approx(Coordinate(17.071067811865476, 27.071067811865476))
    assert Coordinate(10, 20) + Coordinate(1, 2) == Coordinate(11, 22)

    coord = Coordinate(1, 2)
    with raises(ValueError):
        coord + DirectionalOffset("INVALID_DIRECTION", 1)  # type: ignore
    with raises(NotImplementedError):
        coord + "INVALID"  # type: ignore


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


def test_polygon() -> None:
    with raises(ValueError):
        Polygon([])
    polygon = Polygon([Coordinate(0, 0), Coordinate(1, 0), Coordinate(1, 1)])
    assert polygon.rectangle == Rectangle(Coordinate(0, 0), Size(1, 1))
