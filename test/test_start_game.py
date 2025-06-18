from unittest.mock import MagicMock, Mock

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
    clock.tick.side_effect = lambda _: mocker.patch(
        "pygame.event.get", lambda: [Event(QUIT)]
    )

    game = Game.load(get_scene_mock, clock)
    set_caption.assert_called_once_with("Test")
    get_scene_mock.assert_called_once()

    mocker.patch(
        "pygame.event.get",
        lambda: [Event(KEYDOWN, key=K_LEFT), Event(VIDEORESIZE, w=200, h=300)],
    )

    game.start()
    clock.get_time.assert_called_once()
    blits = set_mode.return_value.blits
    # invoke generator
    list(blits.call_args[0][0])
    blits.assert_called_once()
    flip.assert_called_once()
    clock.tick.assert_called_once_with(60)
