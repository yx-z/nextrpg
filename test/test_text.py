from nextrpg.draw_on_screen import Coordinate
from nextrpg.text import Text


def test_text():
    assert Text("a", Coordinate(0, 0)).draw_on_screen