from pathlib import Path

from pygame import Color, Surface
from pygame.locals import SRCALPHA
from pytest_mock import MockerFixture

from nextrpg import (
    Config,
    Coordinate,
    DebugConfig,
    Draw,
    DrawOnScreen,
    PolygonOnScreen,
    RectangleOnScreen,
    Rgba,
    Size,
    override_config,
)
from test.util import MockSurface


def test_draw(mocker: MockerFixture) -> None:
    surf = MockSurface()
    assert Draw(surf)._surface

    mocker.patch("nextrpg.draw.draw.load")
    assert Draw(Path("abc"))._surface
    draw = Draw(Surface((1, 2), SRCALPHA))
    assert draw.width == 1
    assert draw.height == 2
    assert draw.size == Size(1, 2)
    assert draw.crop(Coordinate(0, 0), Size(1, 2)).size == Size(1, 2)
    assert isinstance(draw.pygame, Surface)

    assert draw.set_alpha(0) is not draw

    with override_config(
        Config(debug=DebugConfig(draw_background_color=Rgba(0, 0, 255, 32)))
    ):
        surface = Draw(Surface((1, 2), SRCALPHA)).pygame
        assert isinstance(surface, Surface)
        assert surface.get_at((0, 0)) == Color(0, 0, 255, 32)


def test_draw_on_screen() -> None:
    draw_on_screen = DrawOnScreen(Coordinate(10, 20), Draw(Surface((1, 2))))
    assert draw_on_screen.rectangle_on_screen == RectangleOnScreen(
        Coordinate(10, 20), Size(1, 2)
    )
    assert draw_on_screen.visible_rectangle_on_screen
    surface, coord = draw_on_screen.pygame
    assert isinstance(surface, Surface)
    assert coord == (10, 20)
    assert (draw_on_screen + Coordinate(1, 2)).top_left == Coordinate(11, 22)
    assert draw_on_screen - Coordinate(1, 2)


def test_polygon() -> None:
    polygon = PolygonOnScreen(
        (Coordinate(0, 0), Coordinate(1, 0), Coordinate(1, 1))
    )
    assert polygon.bounding_rectangle == RectangleOnScreen(
        Coordinate(0, 0), Size(1, 1)
    )

    assert polygon.collide(
        PolygonOnScreen((Coordinate(0, 0), Coordinate(1, 2), Coordinate(1, 1)))
    )
    assert not polygon.collide(
        PolygonOnScreen(
            (Coordinate(10, 20), Coordinate(21, 20), Coordinate(20, 20))
        )
    )
    assert polygon.contain(Coordinate(0.5, 0.5))
    assert not polygon.contain(Coordinate(10, 20))
    assert polygon.length
    assert PolygonOnScreen(
        (Coordinate(10, 20), Coordinate(21, 20), Coordinate(20, 20)),
        closed=False,
    ).length
    assert polygon.line(Rgba(0, 0, 0, 0), 2)
    assert polygon.line(Rgba(0, 0, 0, 0))
    assert polygon - Coordinate(1, 2)


def test_rectangle() -> None:
    rect = RectangleOnScreen(Coordinate(10, 20), Size(2, 2))
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
    assert rect.collide(RectangleOnScreen(Coordinate(9, 20), Size(10, 20)))
    assert rect.contain(Coordinate(11, 21))
    assert rect.collide(
        PolygonOnScreen(
            (Coordinate(10, 20), Coordinate(11, 20), Coordinate(11, 21))
        )
    )
    assert RectangleOnScreen(Coordinate(0, 0), Size(1, 2)).fill(
        Rgba(0, 0, 0, 0)
    ).top_left == Coordinate(0, 0)
    assert RectangleOnScreen(Coordinate(0, 0), Size(0, 0)).fill(
        Rgba(0, 0, 0, 0)
    ).visible_rectangle_on_screen.size == Size(0, 0)
    assert rect + Coordinate(1, 2)
