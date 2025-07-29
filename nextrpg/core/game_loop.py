from dataclasses import KW_ONLY, field, replace
from typing import Self
from collections.abc import Callable

import pygame
from pygame import Clock

from nextrpg.core.dataclass_with_instance_init import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.core.logger import Logger
from nextrpg.event.pygame_event import PygameEvent, Quit, to_typed_event
from nextrpg.global_config.global_config import config
from nextrpg.gui.window import Window
from nextrpg.scene.scene import Scene

logger = Logger("Game")


@dataclass_with_instance_init(frozen=True)
class GameLoop:

    entry_scene: Callable[[], Scene]
    _: KW_ONLY = not_constructor_below()
    running: bool = True
    _clock: Clock = field(default_factory=Clock)
    _window: Window = field(default_factory=Window)
    _scene: Scene = instance_init(lambda self: self.entry_scene())

    @property
    def tick(self) -> Self:
        logger.debug(t"FPS: {self._clock.get_fps():.0f}", duration=None)
        self._clock.tick(config().gui.frames_per_second)
        time_delta = self._clock.get_time()

        window = self._window.update
        window.draw(self._scene.draw_on_screens, time_delta)

        logger.debug(t"Current scene {type(self._scene)}", duration=None)
        loop = replace(
            self, _scene=self._scene.tick(time_delta), _window=window
        )
        for e in pygame.event.get():
            loop = loop._event(to_typed_event(e))
        return loop

    def _event(self, e: PygameEvent) -> Self:
        return replace(
            self,
            _scene=self._scene.event(e),
            _window=self._window.event(e),
            running=not isinstance(e, Quit),
        )
