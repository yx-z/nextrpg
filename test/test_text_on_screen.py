from pytest_mock import MockerFixture

from nextrpg import Coordinate, Text, TextOnScreen


def test_text_on_screen(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.core.font.Font.pygame")
    assert TextOnScreen(Coordinate(0, 0), Text("a")).draw_on_screens
