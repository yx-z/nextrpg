from collections.abc import Callable
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import Self

import pygame
from pygame.time import Clock

from nextrpg.config.config import config
from nextrpg.config.system.game_loop_config import GameLoopConfig
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

_last_scene: Scene | None = None


def last_scene() -> Scene:
    assert _last_scene, "Cannot call `last_scene` before `GameLoop.tick`."
    return _last_scene


@dataclass_with_default(frozen=True)
class GameLoop:
    entry_scene: Callable[[], Scene]
    _: KW_ONLY = private_init_below()
    running: bool = True
    _clock: Clock = field(default_factory=Clock)
    _window: Window = field(default_factory=Window)
    _scene: Scene = default(lambda self: self.entry_scene())
    _config: GameLoopConfig = field(default_factory=lambda: config().game_loop)

    @cached_property
    def tick(self) -> GameLoop:
        fps_info = f"FPS: {self._clock.get_fps():.0f}"
        log.debug(t"{type_name(self._scene)} {fps_info}", duration=None)

        max_fps = self._config.max_frames_per_second
        self._clock.tick(max_fps)
        time_delta = self._clock.get_time()

        window = self._window.tick(fps_info)
        window.blits(self._scene.drawing_on_screens, time_delta)

        global _last_scene
        _last_scene = self._scene
        ticked_scene = self._scene.tick(time_delta)

        loop = replace(self, _scene=ticked_scene, _window=window)
        for pygame_event in pygame.event.get():
            io_event = to_io_event(pygame_event)
            loop = loop._event(io_event)
        return loop

    def _event(self, e: IoEvent) -> Self:
        scene = self._scene.event(e)
        window = self._window.event(e)
        running = not isinstance(e, Quit)
        return replace(self, _scene=scene, _window=window, running=running)
