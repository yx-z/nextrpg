"""
Start the game window and game loop.
"""

from asyncio import sleep
from dataclasses import KW_ONLY, dataclass, replace
from functools import singledispatchmethod
from typing import Callable, Self

import pygame
from pygame.time import Clock

from nextrpg.config import config
from nextrpg.core import INTERNAL, initialize_internal_field
from nextrpg.event.pygame_event import (
    PygameEvent,
    Quit,
    to_typed_event,
)
from nextrpg.gui import Gui
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
            self._step()

    async def start_async(self) -> None:
        """
        Start the game in async fashion in the context of pygbag/web.
        """
        while self._loop.is_running:
            self._step()
            await sleep(0)

    def _step(self) -> None:
        self._loop = self._loop.tick().step().draw()
        assert callable(self._loop.event)
        for e in pygame.event.get():
            self._loop = self._loop.event(to_typed_event(e))

@dataclass(frozen=True)
class _GameLoop:
    entry_scene: Callable[[], Scene]
    is_running: bool = True
    _: KW_ONLY = INTERNAL
    _clock: Clock = INTERNAL
    _gui: Gui = INTERNAL
    _scene: Scene = INTERNAL

    def tick(self) -> Self:
        self._clock.tick(config().gui.frames_per_second)
        return self

    @singledispatchmethod
    def event(self, e: PygameEvent) -> "_GameLoop":
        return replace(
            self, _scene=self._scene.event(e), _gui=self._gui.event(e)
        )

    @event.register
    def _quit(self, e: Quit) -> Self:
        return replace(self, _scene=self._scene.event(e), is_running=False)

    def step(self) -> "_GameLoop":
        return replace(self, _scene=self._scene.step(self._clock.get_time()))

    def draw(self) -> Self:
        self._gui.draw(self._scene.draw_on_screens)
        return self

    def __post_init__(self) -> None:
        initialize_internal_field(self, "_gui", Gui)
        initialize_internal_field(self, "_clock", Clock)
        initialize_internal_field(self, "_scene", self.entry_scene)

