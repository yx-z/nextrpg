"""
Start the game window and game loop.
"""

from asyncio import run, sleep
from typing import Callable

import pygame
from pygame import Surface, init
from pygame.display import flip, set_caption, set_mode
from pygame.locals import RESIZABLE
from pygame.time import Clock

from nextrpg.config import config
from nextrpg.event.pygame_event import (
    GuiResize,
    PygameEvent,
    Quit,
    to_typed_event,
)
from nextrpg.gui import Gui
from nextrpg.scene.scene import Scene


class Game:
    """
    Game instance that manages the game loop and the game window.
    """

    def __init__(
        self,
        entry_scene: Callable[[], Scene],
        clock: Clock | None = None,
        gui: Gui | None = None,
    ) -> None:
        """
        Sets up a game window, loads the entry scene.

        Args:
            `entry_scene`: A function that returns the entry scene.
                This has to be a function but not a direct `Scene` instance,
                because drawings can only be loaded after pygame initialization.

            `clock`: A ticking clock controlling the game loop.
                If `None`, default to `pygame.Clock`.

            `gui`: A `Gui` instance for scaling and centering drawings.
                If `None`, default to `Gui` from `config()`.
        """
        self._screen = _init_screen()
        self._scene = entry_scene()
        self._clock = clock or Clock()
        self._gui = gui or Gui()

    def start(self) -> None:
        """
        Start the game in a local pygame window.
        """
        run(self.start_async())

    async def start_async(self) -> None:
        """
        Start the game in async fashion in the context of pygbag/web.
        """
        while self._step():
            await sleep(0)

    def _step(self) -> bool:
        self._clock.tick(config().gui.frames_per_second)
        self._draw()
        return all(map(self._event, map(to_typed_event, pygame.event.get())))

    def _event(self, event: PygameEvent) -> bool:
        self._scene = self._scene.event(event)
        match event:
            case Quit():
                return False
            case GuiResize() as gui:
                self._gui = Gui(gui.size)
        return True

    def _draw(self) -> None:
        self._scene = self._scene.step(self._clock.get_time())
        self._screen.fill(config().gui.background_color.tuple)
        self._screen.blit(*self._gui.scale(self._scene.draw_on_screens))
        flip()


def _init_screen() -> Surface:
    init()
    set_caption(config().gui.title)
    return set_mode(
        config().gui.size.tuple, RESIZABLE if config().gui.resize else 0
    )
