from pytest_mock import MockerFixture

from nextrpg.draw.coordinate import Coordinate
from nextrpg.draw.text import Text
from nextrpg.draw.text_on_screen import TextOnScreen


def test_text_on_screen(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.core.Font.pygame")
    assert TextOnScreen(Text("a"), Coordinate(0, 0)).draw_on_screen
