from unittest.mock import MagicMock, Mock

import pygame
from pygame import Event, KEYDOWN, K_LEFT, QUIT, VIDEORESIZE
from pytest_mock import MockerFixture

from nextrpg.config import Config, GuiConfig, set_config
from nextrpg.draw_on_screen import Size
from nextrpg.scene.scene import Scene
from nextrpg.start_game import start_game


def test_start_game(mocker: MockerFixture) -> None:
    init = Mock()
    mocker.patch("nextrpg.start_game.init", init)
    flip = Mock()
    mocker.patch("nextrpg.start_game.flip", flip)
    set_caption = Mock()
    mocker.patch("nextrpg.start_game.set_caption", set_caption)
    set_mode = Mock()
    mocker.patch("nextrpg.start_game.set_mode", set_mode)
    clock = Mock()
    mocker.patch("nextrpg.start_game.Clock", clock)
    clock_instance = clock.return_value
    clock_instance.tick.side_effect = lambda _: mocker.patch(
        "pygame.event.get", lambda: [Event(QUIT)]
    )
    mocker.patch(
        "pygame.event.get",
        lambda: [Event(KEYDOWN, key=K_LEFT), Event(VIDEORESIZE, w=200, h=300)],
    )
    scene = MagicMock()
    draw_on_screen = MagicMock()
    scene.draw_on_screen.return_value = [draw_on_screen]

    set_config(
        Config(
            gui=GuiConfig(
                title="Test",
                size=Size(100, 100),
                frames_per_second=60,
                resize=True,
            )
        )
    )

    def get_scene() -> Scene:
        init.assert_called_once()
        set_mode.assert_called_once_with((100, 100), pygame.RESIZABLE)
        return scene

    get_scene_mock = Mock(side_effect=get_scene)
    start_game(get_scene_mock)
    set_caption.assert_called_once_with("Test")
    get_scene_mock.assert_called_once()

    clock_instance.get_time.assert_called_once()
    blits = set_mode.return_value.blits
    # invoke generator
    list(blits.call_args[0][0])
    blits.assert_called_once()
    flip.assert_called_once()
    clock_instance.tick.assert_called_once_with(60)
