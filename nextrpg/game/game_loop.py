import gc
from collections.abc import Callable
from dataclasses import KW_ONLY, field, replace
from typing import Self

import pygame
from pygame import Clock

from nextrpg.config.config import config
from nextrpg.config.game_loop_config import GameLoopConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
    type_name,
)
from nextrpg.core.log import Log
from nextrpg.event.io_event import IoEvent, Quit, to_io_event
from nextrpg.gui.window import Window
from nextrpg.scene.scene import Scene

log = Log()


@dataclass_with_default(frozen=True)
class GameLoop:
    entry_scene: Callable[[], Scene]
    _: KW_ONLY = private_init_below()
    running: bool = True
    _clock: Clock = field(default_factory=Clock)
    _window: Window = field(default_factory=Window)
    _scene: Scene = default(lambda self: self.entry_scene())
    _config: GameLoopConfig = field(default_factory=lambda: config().game_loop)
    __: None = default(
        lambda self: (
            gc.disable()
            if self._config.garbage_collect_time_threshold
            else None
        )
    )

    @property
    def tick(self) -> GameLoop:
        if (
            self._config.garbage_collect_time_threshold
            and self._clock.get_time()
            < self._config.garbage_collect_time_threshold
        ):
            gc.collect()

        fps_info = f"FPS: {self._clock.get_fps():.0f}"
        log.debug(t"{type_name(self._scene)} {fps_info}", duration=None)

        max_fps = config().game_loop.max_frames_per_second
        self._clock.tick(max_fps)
        time_delta = self._clock.get_time()

        window = self._window.tick(fps_info)
        window.blits(self._scene.drawing_on_screens, time_delta)

        ticked_scene = self._scene.tick(time_delta)
        loop = replace(self, _scene=ticked_scene, _window=window)
        for e in pygame.event.get():
            loop = loop._event(to_io_event(e))
        return loop

    def _event(self, e: IoEvent) -> Self:
        scene = self._scene.event(e)
        window = self._window.event(e)
        running = not isinstance(e, Quit)
        return replace(self, _scene=scene, _window=window, running=running)
