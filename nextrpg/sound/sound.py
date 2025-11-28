from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from pathlib import Path
from typing import Self

import pygame

from nextrpg.config.config import config
from nextrpg.config.system.sound_config import SoundConfig
from nextrpg.core.cached_decorator import cached
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)


@cached(lambda resource_config: resource_config.sound_cache_size)
@dataclass_with_default(frozen=True)
class _Sound:
    file: str | Path
    pygame: pygame.Sound = default(lambda self: self._init_loaded)

    @property
    def _init_loaded(self) -> pygame.Sound:
        return pygame.Sound(self.file)


@dataclass_with_default(frozen=True)
class Sound:
    file: str | Path
    loop: bool = False
    config: SoundConfig = field(default_factory=lambda: config().system.sound)
    _: KW_ONLY = private_init_below()
    started: bool = False
    _sound: _Sound = default(lambda self: _Sound(self.file))

    def play(self) -> Self:
        if not self.started:
            self._sound.pygame.play(
                self._loop, fade_ms=self.config.fade_in_duration
            )
        return replace(self, started=True)

    def stop(self) -> Self:
        if self.started:
            self._sound.pygame.fadeout(self.config.fade_out_duration)
        return replace(self, started=False)

    @cached_property
    def _loop(self) -> int:
        if self.loop:
            return -1
        return 0
