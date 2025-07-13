"""
Start the game window and game loop.
"""

from asyncio import sleep
from dataclasses import field, replace
from functools import cached_property
from typing import Callable, Self

import pygame
from pygame.time import Clock

from nextrpg.config.config import config
from nextrpg.event.pygame_event import PygameEvent, Quit, to_typed_event
from nextrpg.gui.window import Gui
from nextrpg.logger import Logger
from nextrpg.model import dataclass_with_instance_init, instance_init
from nextrpg.scene.scene import Scene

logger = Logger("Game")


@dataclass_with_instance_init
class Game:
    """
    Sets up a game window, loads the entry scene.

    Arguments:
        `entry_scene`: A function that returns the entry scene.
            This has to be a function but not a direct `Scene` instance,
            because drawings can only be loaded after pygame initialization.
    """

    entry_scene: Callable[[], Scene]
    _loop: _GameLoop = instance_init(
        lambda self: _GameLoop(entry_scene=self.entry_scene)
    )

    def start(self) -> None:
        """
        Start the game in a local pygame window.
        """
        while self._loop.running:
            self._tick()

    async def start_async(self) -> None:
        """
        Start the game in async fashion in the context of pygbag/web.
        """
        while self._loop.running:
            self._tick()
            await sleep(0)

    def _tick(self) -> None:
        object.__setattr__(self, "_loop", self._loop.tick())


@dataclass_with_instance_init
class _GameLoop:
    entry_scene: Callable[[], Scene]
    running: bool = True
    _clock: Clock = field(default_factory=Clock)
    _gui: Gui = field(default_factory=Gui)
    _scene: Scene = instance_init(lambda self: self.entry_scene())

    def tick(self) -> Self:
        logger.debug(t"FPS: {self._clock.get_fps():.0f}", duration=None)
        self._clock.tick(config().gui.frames_per_second)
        time_delta = self._clock.get_time()

        self._gui.draw(self._scene.draw_on_screens, time_delta)

        loop = replace(
            self, _scene=self._scene.tick(time_delta), _gui=self._update_gui
        )
        for e in pygame.event.get():
            loop = loop._event(to_typed_event(e))
        return loop

    def _event(self, e: PygameEvent) -> Self:
        return replace(
            self,
            _scene=self._scene.event(e),
            _gui=self._gui.event(e),
            running=not isinstance(e, Quit),
        )

    @cached_property
    def _update_gui(self) -> Gui:
        if config().gui is self._gui.current_config:
            return self._gui
        return replace(
            self._gui,
            current_config=config().gui,
            last_config=self._gui.current_config,
        )
