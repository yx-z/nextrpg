from dataclasses import dataclass

from nextrpg.core.time import Millisecond


@dataclass(frozen=True, slots=True)
class TransitionConfig:
    duration: Millisecond = 500
