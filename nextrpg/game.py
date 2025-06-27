"""
Start the game window and game loop.
"""

from __future__ import annotations

from asyncio import sleep
from dataclasses import KW_ONLY, field, replace
from functools import cached_property, reduce, singledispatchmethod
from typing import Callable

import pygame
from pygame.time import Clock

from nextrpg.config import config
from nextrpg.event.pygame_event import (
    PygameEvent,
    Quit,
    to_typed_event,
)
from nextrpg.gui import Gui
from nextrpg.model import Model, internal_field
from nextrpg.scene.scene import Scene


class Game:
    """
    Game entry point.
    """

    def __init__(self, entry_scene: Callable[[], Scene]) -> None:
        """
        Sets up a game window, loads the entry scene.

        Args:
            `entry_scene`: A function that returns the entry scene.
                This has to be a function but not a direct `Scene` instance,
                because drawings can only be loaded after pygame initialization.
        """
        self._loop = _GameLoop(entry_scene)

    def start(self) -> None:
        """
        Start the game in a local pygame window.
        """
        while self._loop.is_running:
            self._loop = self._loop.step()

    async def start_async(self) -> None:
        """
        Start the game in async fashion in the context of pygbag/web.
        """
        while self._loop.is_running:
            self._loop = self._loop.step()
            await sleep(0)


class _GameLoop(Model):
    entry_scene: Callable[[], Scene]
    _: KW_ONLY = field()
    _is_running: bool = internal_field(True)
    _clock: Clock = internal_field(Clock)
    _gui: Gui = internal_field(Gui)
    _scene: Scene = internal_field(lambda self: self.entry_scene())

    @cached_property
    def is_running(self) -> bool:
        return self._is_running

    @singledispatchmethod
    def event(self, e: PygameEvent) -> _GameLoop:
        return replace(
            self, _scene=self._scene.event(e), _gui=self._gui.event(e)
        )

    def step(self) -> _GameLoop:
        self._clock.tick(config().gui.frames_per_second)
        stepped = replace(self, _scene=self._scene.step(self._clock.get_time()))
        self._gui.draw(self._scene.draw_on_screens)
        assert callable(self.event)
        return reduce(
            lambda loop, e: loop.event(to_typed_event(e)),
            pygame.event.get(),
            stepped,
        )


@_GameLoop.event.register
def _quit(self, e: Quit) -> _GameLoop:
    return replace(self, _scene=self._scene.event(e), _is_running=False)
