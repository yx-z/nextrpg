from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from nextrpg.config.system.audio_config import AudioConfig


@dataclass(frozen=True)
class AudioSpec:
    file: str | Path
    loop: bool
    config: AudioConfig

    @cached_property
    def loop_flag(self) -> int:
        if self.loop:
            return -1
        return 0

    def __eq__(self, other: AudioSpec) -> bool:
        return self._tuple == other._tuple

    def __hash__(self) -> int:
        return hash(self._tuple)

    @cached_property
    def _tuple(self) -> tuple[str, bool, AudioConfig]:
        return str(self.file), self.loop, self.config
