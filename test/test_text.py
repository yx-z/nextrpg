from pytest_mock import MockerFixture

from nextrpg.draw.coordinate import Coordinate
from nextrpg.draw.text import Text


def test_text(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.core.Font.pygame")
    assert Text("a", Coordinate(0, 0)).draw_on_screen
