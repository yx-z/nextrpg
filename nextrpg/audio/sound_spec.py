from dataclasses import dataclass, field

from nextrpg.audio.audio_spec import AudioSpec
from nextrpg.config.config import config
from nextrpg.config.system.audio_config import AudioConfig


@dataclass(frozen=True)
class SoundSpec(AudioSpec):
    loop: bool = False
    config: AudioConfig = field(default_factory=lambda: config().system.sound)
