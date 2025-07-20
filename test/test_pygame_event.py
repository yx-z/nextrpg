from unittest.mock import Mock

from pytest_mock import MockerFixture
from nextrpg import post_quit


def test_post_quit(mocker: MockerFixture) -> None:
    mock = Mock()
    mocker.patch("nextrpg.event.pygame_event.post", mock)
    post_quit()
    mock.assert_called()
