from asyncio import run
from dataclasses import replace
from unittest.mock import AsyncMock, Mock

from pygame.event import Event
from pygame.locals import KEYDOWN, K_LEFT, QUIT, VIDEORESIZE
from pytest_mock import MockerFixture

from nextrpg.game import Game


def test_game(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.game.Gui")
    mocker.patch(
        "pygame.event.get",
        lambda: [
            Event(KEYDOWN, key=K_LEFT),
            Event(VIDEORESIZE, w=200, h=300),
            Event(QUIT),
        ],
    )
    scene = Mock()
    clock = Mock()
    gui = Mock()
    game = Game(lambda: scene)
    game._loop = replace(game._loop, _scene=scene, _clock=clock, _gui=gui)
    game.start()
    scene.step.assert_called_once()
    clock.tick.assert_called_once_with(60)
    gui.event.assert_called_once()
    gui.draw.assert_called_once()

    sleep = AsyncMock()
    game._loop = replace(game._loop, _is_running=True)
    mocker.patch("nextrpg.game.sleep", sleep)
    run(game.start_async())
    sleep.assert_called_once_with(0)
