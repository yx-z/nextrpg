"""
Start the game window and game loop.
"""

from asyncio import run, sleep
from dataclasses import astuple
from typing import Callable

import pygame
from pygame import init
from pygame.constants import RESIZABLE
from pygame.display import flip, set_caption, set_mode
from pygame.time import Clock

from nextrpg.config import config
from nextrpg.event.pygame_event import GuiResize, Quit, to_typed_event
from nextrpg.scene.scene import Scene


def start_game(entry_scene: Callable[[], Scene]) -> None:
    """
    Initializes and starts the game by handling the main game loop.

    This function is the local/normal run entry point for the game.

    Args:
        `entry_scene`: A callable that returns the initial scene
            to be displayed and interacted with when the game starts.

            This is a function because the scene that loads sprites must be
            created after pygame initialization.

    Returns:
        `None`: when the game exits.
    """
    run(async_start_game(entry_scene))


async def async_start_game(entry_scene: Callable[[], Scene]) -> None:
    """
    Initializes and starts the game by handling the main game loop.

    This async function is the web/pygbag entry point for the game.

    Args:
        `entry_scene`: A callable that returns the initial scene
            to be displayed and interacted with when the game starts.

            This is a function because the scene that loads sprites must be
            created after pygame initialization.

    Returns:
        `None`: when the game exits.
    """
    init()
    set_caption(config().gui.title)
    screen = set_mode(
        astuple(config().gui.size),
        RESIZABLE if config().gui.allow_resize else 0,
    )
    scene = entry_scene()
    clock = Clock()
    scale = 1.0
    while True:
        for event in map(to_typed_event, pygame.event.get()):
            scene.event(event)
            match event:
                case Quit():
                    return
                case GuiResize() as g:
                    scale = min(
                        g.size.width / config().gui.size.width,
                        g.size.height / config().gui.size.height,
                    )

        screen.blits(
            (draw_on_screen * scale).pygame
            for draw_on_screen in scene.draw_on_screen(clock.get_time())
        )
        flip()
        clock.tick(config().gui.frames_per_second)
        await sleep(0)
