from dataclasses import KW_ONLY, replace
from pathlib import Path
from typing import Self

import pygame as pg
from pygame import Channel

from nextrpg.audio.sound_spec import SoundSpec
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
    pygame: pg.Sound = default(lambda self: self._init_loaded)

    @property
    def _init_loaded(self) -> pg.Sound:
        return pg.Sound(self.file)


@dataclass_with_default(frozen=True)
class Sound:
    spec: SoundSpec
    _: KW_ONLY = private_init_below()
    _channel: Channel | None = None
    _sound: _Sound = default(lambda self: _Sound(self.spec.file))

    def play(self) -> Self:
        if self._channel:
            return self

        channel = self._sound.pygame.play(
            self.spec.loop_flag, fade_ms=self.spec.config.fade_in_duration
        )
        return replace(self, _channel=channel)

    def stop(self) -> Self:
        if self._channel:
            self._channel.fadeout(self.spec.config.fade_out_duration)
            return replace(self, _channel=None)
        return self
