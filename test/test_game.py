from asyncio import run
from dataclasses import replace
from unittest.mock import AsyncMock, MagicMock, Mock

import pygame
from pygame import Event, KEYDOWN, K_LEFT, QUIT, VIDEORESIZE
from pytest_mock import MockerFixture

from nextrpg.config import Config, GuiConfig
from nextrpg.draw_on_screen import Size
from nextrpg.game import Game
from nextrpg.scene.scene import Scene
from test.util import override_config


@override_config(Config(GuiConfig("Test", Size(100, 100))))
def test_game(mocker: MockerFixture) -> None:
    init = Mock()
    mocker.patch("nextrpg.game.init", init)
    flip = Mock()
    mocker.patch("nextrpg.game.flip", flip)
    set_caption = Mock()
    mocker.patch("nextrpg.game.set_caption", set_caption)
    set_mode = Mock()
    mocker.patch("nextrpg.game.set_mode", set_mode)

    scene = MagicMock()
    draw_on_screen = MagicMock()
    scene.draw_on_screen.return_value = [draw_on_screen]

    def get_scene() -> Scene:
        init.assert_called_once()
        set_mode.assert_called_once_with((100, 100), pygame.RESIZABLE)
        return scene

    get_scene_mock = Mock(side_effect=get_scene)

    clock = Mock()
    game = Game(get_scene_mock, clock)
    set_caption.assert_called_once_with("Test")
    get_scene_mock.assert_called_once()

    mocker.patch(
        "pygame.event.get",
        lambda: [
            Event(KEYDOWN, key=K_LEFT),
            Event(VIDEORESIZE, w=200, h=300),
            Event(QUIT),
        ],
    )

    game.start()
    clock.get_time.assert_called_once()
    set_mode.return_value.blit.assert_called_once()
    flip.assert_called_once()
    clock.tick.assert_called_once_with(60)

    def step() -> None:
        game._loop = replace(game._loop, is_running=False)

    game._step = step
    game._loop = replace(game._loop, is_running=True)
    sleep = AsyncMock()
    mocker.patch("nextrpg.game.sleep", sleep)
    run(game.start_async())
    sleep.assert_called_once_with(0)
