from asyncio import run
from dataclasses import dataclass, replace
from typing import Any, Self
from unittest.mock import AsyncMock, MagicMock, Mock

from pygame.event import Event
from pygame.locals import KEYDOWN, K_LEFT, QUIT, VIDEORESIZE
from pytest_mock import MockerFixture

from nextrpg.game import Game


def test_game(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.game.Gui.__post_init__")
    mocker.patch(
        "pygame.event.get",
        lambda: [
            Event(KEYDOWN, key=K_LEFT),
            Event(VIDEORESIZE, w=200, h=300),
            Event(QUIT),
        ],
    )
    scene = Mock()
    clock = MagicMock()
    clock.get_fps = MagicMock(return_value=60)

    @dataclass
    class MockGui:
        current_config: Mock = Mock()
        last_config: Mock = Mock()
        initial_config: Mock = Mock()
        draw: Mock = Mock()

        def event(self, _: Any) -> Self:
            return self

    gui = MockGui()
    game = Game(lambda: scene)
    game._loop = replace(game._loop, _scene=scene, _clock=clock, _gui=gui)
    game.start()
    scene.step.assert_called_once()
    clock.tick.assert_called_once_with(60)
    gui.draw.assert_called_once()

    sleep = AsyncMock()
    game._loop = replace(game._loop, is_running=True)
    mocker.patch("nextrpg.game.sleep", sleep)
    run(game.start_async())
    sleep.assert_called_once_with(0)
