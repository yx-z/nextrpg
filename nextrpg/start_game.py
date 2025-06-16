"""
Start the game window and game loop.
"""

from asyncio import run, sleep
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

            This is a function because the scene that loads drawings must be
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

            This is a function because the scene that loads drawings must be
            created after pygame initialization.

    Returns:
        `None`: when the game exits.
    """
    init()
    set_caption(config().gui.title)
    screen = set_mode(
        config().gui.size.tuple, RESIZABLE if config().gui.resize else 0
    )
    scene = entry_scene()
    clock = Clock()
    scale = 1.0
    while True:
        for event in map(to_typed_event, pygame.event.get()):
            scene = scene.event(event)
            match event:
                case Quit():
                    return
                case GuiResize() as g:
                    scale = min(
                        g.size.width / config().gui.size.width,
                        g.size.height / config().gui.size.height,
                    )

        scene = scene.step(clock.get_time())
        screen.fill(config().gui.background_color.tuple)
        screen.blits((d * scale).pygame for d in scene.draw_on_screen)
        flip()
        clock.tick(config().gui.frames_per_second)
        await sleep(0)
