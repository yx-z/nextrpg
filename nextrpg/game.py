"""
Start the game window and game loop.
"""

from asyncio import sleep
from dataclasses import dataclass, replace
from functools import singledispatchmethod
from typing import Callable, Self

import pygame
from pygame import Surface, init
from pygame.display import flip, set_caption, set_mode
from pygame.locals import RESIZABLE
from pygame.time import Clock

from nextrpg.config import config
from nextrpg.core import INTERNAL_ONLY, init_internal_field
from nextrpg.event.pygame_event import (
    GuiResize,
    PygameEvent,
    Quit,
    to_typed_event,
)
from nextrpg.gui import Gui
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class _GameLoop:
    entry_scene: Callable[[], Scene]
    is_running: bool = True
    _clock: Clock = INTERNAL_ONLY
    _gui: Gui = INTERNAL_ONLY
    _screen: Surface = INTERNAL_ONLY
    _scene: Scene = INTERNAL_ONLY

    def tick(self) -> None:
        self._clock.tick(config().gui.frames_per_second)

    @singledispatchmethod
    def event(self, e: PygameEvent) -> "_GameLoop":
        return replace(self, _scene=self._scene.event(e))

    @event.register
    def _resize(self, e: GuiResize) -> Self:
        return replace(self, _gui=Gui(e.size))

    @event.register
    def _quit(self, _: Quit) -> Self:
        return replace(self, is_running=False)

    def draw(self) -> "_GameLoop":
        scene = self._scene.step(self._clock.get_time())
        self._screen.fill(config().gui.background_color.tuple)
        self._screen.blit(*self._gui.scale(self._scene.draw_on_screens).pygame)
        flip()
        return replace(self, _scene=scene)

    def __post_init__(self) -> None:
        init_internal_field(self, "_gui", Gui)
        init_internal_field(self, "_clock", Clock)
        init_internal_field(self, "_screen", _init_screen)
        init_internal_field(self, "_scene", self.entry_scene)


class Game:
    """
    Game entry point.
    """

    def __init__(
        self, entry_scene: Callable[[], Scene], clock: Clock | None = None
    ) -> None:
        """
        Sets up a game window, loads the entry scene.

        Args:
            `entry_scene`: A function that returns the entry scene.
                This has to be a function but not a direct `Scene` instance,
                because drawings can only be loaded after pygame initialization.

            `clock`: A ticking clock controlling the game loop.
                If `None`, default to `pygame.Clock()`.
        """
        self._loop = _GameLoop(entry_scene, _clock=clock or Clock())

    def start(self) -> None:
        """
        Start the game in a local pygame window.
        """
        while self._loop.is_running:
            self._step()

    async def start_async(self) -> None:
        """
        Start the game in async fashion in the context of pygbag/web.
        """
        while self._loop.is_running:
            self._step()
            await sleep(0)

    def _step(self) -> None:
        self._loop.tick()
        self._loop = self._loop.draw()
        for e in pygame.event.get():
            self._loop = self._loop.event(to_typed_event(e))


def _init_screen() -> Surface:
    init()
    set_caption(config().gui.title)
    return set_mode(
        config().gui.size.tuple, RESIZABLE if config().gui.resize else 0
    )
