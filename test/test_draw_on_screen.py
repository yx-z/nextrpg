from pygame import Color, SRCALPHA, Surface

from nextrpg.common_types import Coordinate, Rectangle, Size
from nextrpg.config import Config, DebugConfig, config, set_config
from nextrpg.draw_on_screen import DrawOnScreen, Drawing


def test_drawing() -> None:
    drawing = Drawing(Surface((1, 2), SRCALPHA))
    assert drawing.width == 1
    assert drawing.height == 2
    assert drawing.size == Size(1, 2)
    assert drawing.crop(Coordinate(0, 0), Size(1, 2)).size == Size(1, 2)
    assert (drawing * 10).size == Size(10, 20)
    assert isinstance(drawing.pygame, Surface)

    prev_config = config()
    try:
        debug = DebugConfig()
        set_config(Config(debug=debug))
        assert isinstance((surface := drawing.pygame), Surface)
        assert surface.get_at((0, 0)) == Color(0, 0, 255, 64)
    finally:
        set_config(prev_config)


def test_draw_on_screen() -> None:
    draw_on_screen = DrawOnScreen(Coordinate(10, 20), Drawing(Surface((1, 2))))
    assert draw_on_screen.rectangle == Rectangle(Coordinate(10, 20), Size(1, 2))
    surface, coord = draw_on_screen.pygame
    assert isinstance(surface, Surface)
    assert coord == (10, 20)
    scaled = draw_on_screen * 2
    assert scaled.drawing.size == Size(2, 4)
    assert scaled.top_left == Coordinate(20, 40)

    drawn = DrawOnScreen.from_rectangle(Rectangle(Coordinate(0, 0), Size(1, 2)))
    assert drawn.top_left == Coordinate(0, 0)
