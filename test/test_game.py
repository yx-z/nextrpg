from asyncio import run
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Any, Self
from unittest.mock import AsyncMock, MagicMock, Mock

from pygame.event import Event
from pygame.locals import K_LEFT, KEYDOWN, QUIT, VIDEORESIZE
from pytest_mock import MockerFixture

from nextrpg import Game


def test_game(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.game.Window.__post_init__")
    mocker.patch(
        "pygame.event.get",
        lambda: (
            Event(KEYDOWN, key=K_LEFT),
            Event(VIDEORESIZE, w=200, h=300),
            Event(QUIT),
        ),
    )
    scene = Mock()
    clock = MagicMock()
    clock.get_fps = MagicMock(return_value=60)

    @dataclass(frozen=True)
    class MockGui:
        current_config: Mock = Mock()
        last_config: Mock = Mock()
        initial_config: Mock = Mock()
        draw: Mock = Mock()

        @cached_property
        def update(self) -> Self:
            return self

        def event(self, _: Any) -> Self:
            return self

    window = MockGui()
    game = Game(entry_scene=lambda: scene)
    object.__setattr__(
        game,
        "_loop",
        replace(game._loop, _scene=scene, _clock=clock, _window=window),
    )
    game.start()
    scene.tick.assert_called_once()
    clock.tick.assert_called_once_with(60)
    window.draw.assert_called_once()

    sleep = AsyncMock()
    object.__setattr__(game, "_loop", replace(game._loop, running=True))
    mocker.patch("nextrpg.game.sleep", sleep)
    run(game.start_async())
    sleep.assert_called_once_with(0)
