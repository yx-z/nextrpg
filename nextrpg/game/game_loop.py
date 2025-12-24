import logging
from collections.abc import Callable
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import Self

from pygame import Clock

from nextrpg.audio.play_music_event import PlayMusicEvent
from nextrpg.config.config import config, force_debug_config, set_config
from nextrpg.config.system.game_loop_config import GameLoopConfig
from nextrpg.config.system.key_mapping_config import KeyMappingConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.logger import Logger
from nextrpg.core.util import type_name
from nextrpg.event.base_event import BaseEvent
from nextrpg.event.event_queue import EventQueue
from nextrpg.event.io_event import Quit, is_key_press
from nextrpg.game.game_state import GameState
from nextrpg.gui.window import Window
from nextrpg.scene.scene import Scene

logger = Logger("loop")

_last_scene: Scene | None = None


def last_scene() -> Scene:
    assert _last_scene, "Cannot call `last_scene` before `GameLoop.tick`."
    return _last_scene


@dataclass_with_default(frozen=True)
class GameLoop:
    entry_scene: Callable[[], Scene]
    state: GameState
    _: KW_ONLY = private_init_below()
    running: bool = True
    _clock: Clock = field(default_factory=Clock)
    _window: Window = field(default_factory=Window)
    _scene: Scene = default(lambda self: self.entry_scene())
    _config: GameLoopConfig = field(
        default_factory=lambda: config().system.game_loop
    )
    _event_queue: EventQueue = EventQueue()

    @cached_property
    def tick(self) -> GameLoop:
        loop = self
        state = self.state
        for event in loop._event_queue:
            loop = loop._event(event, state)

        fps = f"{self._clock.get_fps():.0f}"
        logger.debug(f"FPS: {type_name(self._scene)} {fps}", duration=None)
        ticked_window = loop._window.tick(fps)
        time_delta = loop._clock.tick(loop._config.max_frames_per_second)
        loop._window.blits(loop._scene.drawing_on_screens, time_delta)

        ticked_scene, state = loop._scene.tick(time_delta, state)
        event_queue = loop._event_queue.tick(time_delta, state)
        loop = replace(
            loop,
            state=state,
            _scene=ticked_scene,
            _window=ticked_window,
            _event_queue=event_queue,
        )

        global _last_scene
        _last_scene = self._scene
        return loop

    def _event(self, event: BaseEvent, state: GameState) -> Self:
        if isinstance(event, PlayMusicEvent):
            event()
        if is_key_press(event, KeyMappingConfig.debug_toggle):
            _toggle_debug()
        scene, updated_state = self._scene.event(event, state)
        window = self._window.event(event)
        running = not isinstance(event, Quit)
        return replace(
            self,
            _scene=scene,
            _window=window,
            running=running,
            state=updated_state,
        )


def _toggle_debug() -> None:
    if (cfg := config()).debug:
        cfg = replace(cfg, debug=None)
    else:
        debug = force_debug_config()
        if logging_config := debug.logging:
            logging.basicConfig(
                level=logging_config.level.stdlib,
                **logging_config.console_logger_kwargs,
            )
        cfg = replace(cfg, debug=debug)
    set_config(cfg)
