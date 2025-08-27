from __future__ import annotations

from collections.abc import Callable
from dataclasses import KW_ONLY, field, replace
from typing import Self

import pygame
from pygame import Clock

from nextrpg.core.dataclass_with_default_init import (
    dataclass_with_default_init,
    default_init,
    not_constructor_below,
)
from nextrpg.core.log import Log
from nextrpg.event.pygame_event import PygameEvent, Quit, to_typed_event
from nextrpg.global_config.global_config import config
from nextrpg.gui.window import Window
from nextrpg.scene.scene import Scene

log = Log()


@dataclass_with_default_init(frozen=True)
class GameLoop:
    entry_scene: Callable[[], Scene]
    _: KW_ONLY = not_constructor_below()
    running: bool = True
    _clock: Clock = field(default_factory=Clock)
    _window: Window = field(default_factory=Window)
    _scene: Scene = default_init(lambda self: self.entry_scene())

    @property
    def tick(self) -> GameLoop:
        fps_info = f"FPS: {self._clock.get_fps():.0f}"
        log.debug(fps_info, duration=None)

        # "<'package.my_class'>" -> "my_class"
        scene_type = str(type(self._scene))[2:-2].split(".")[-1]
        log.debug(t"Current scene {scene_type}", duration=None)

        self._clock.tick(config().game_loop.max_frames_per_second)
        time_delta = self._clock.get_time()

        window = self._window.tick(fps_info)
        window.blits(self._scene.drawing_on_screens, time_delta)

        ticked_scene = self._scene.tick(time_delta)
        loop = replace(self, _scene=ticked_scene, _window=window)
        for e in pygame.event.get():
            loop = loop._event(to_typed_event(e))
        return loop

    def _event(self, e: PygameEvent) -> Self:
        scene = self._scene.event(e)
        window = self._window.event(e)
        running = not isinstance(e, Quit)
        return replace(self, _scene=scene, _window=window, running=running)
