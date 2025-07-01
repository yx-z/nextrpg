"""
Start the game window and game loop.
"""

from asyncio import sleep
from dataclasses import field, replace
from functools import reduce, singledispatchmethod
from typing import Callable

import pygame
from pygame.time import Clock

from nextrpg.config import config
from nextrpg.event.pygame_event import PygameEvent, Quit, to_typed_event
from nextrpg.gui import Gui
from nextrpg.logger import debug_log
from nextrpg.model import instance_init, register_instance_init
from nextrpg.scene.scene import Scene


@register_instance_init
class Game:
    """
    Sets up a game window, loads the entry scene.

    Arguments:
        `entry_scene`: A function that returns the entry scene.
            This has to be a function but not a direct `Scene` instance,
            because drawings can only be loaded after pygame initialization.
    """

    entry_scene: Callable[[], Scene]
    _loop: _GameLoop = instance_init(lambda self: _GameLoop(self.entry_scene))

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


@register_instance_init
class _GameLoop:
    entry_scene: Callable[[], Scene]
    is_running: bool = True
    _clock: Clock = field(default_factory=Clock)
    _gui: Gui = field(default_factory=Gui)
    _scene: Scene = instance_init(lambda self: self.entry_scene())

    @singledispatchmethod
    def event(self, e: PygameEvent) -> _GameLoop:
        return replace(
            self, _scene=self._scene.event(e), _gui=self._gui.event(e)
        )

    def step(self) -> _GameLoop:
        debug_log(f"FPS: {self._clock.get_fps():.0f} ")
        self._clock.tick(config().gui.frames_per_second)
        if config().gui is not self._gui.current_config:
            self._gui = replace(
                self._gui,
                current_config=config().gui,
                last_config=self._gui.current_config,
            )
        self._gui.draw(self._scene.draw_on_screens)
        return reduce(
            lambda loop, e: loop.event(to_typed_event(e)),
            pygame.event.get(),
            replace(self, _scene=self._scene.step(self._clock.get_time())),
        )


@_GameLoop.event.register
def _quit(self, e: Quit) -> _GameLoop:
    return replace(self, _scene=self._scene.event(e), is_running=False)
