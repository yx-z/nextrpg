from dataclasses import dataclass

from nextrpg.core.time import Millisecond


@dataclass(frozen=True)
class RpgMakerCharacterDrawingConfig:
    duration_per_frame: Millisecond = 100
