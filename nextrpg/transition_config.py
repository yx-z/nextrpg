from dataclasses import dataclass

from nextrpg.model import export
from nextrpg.core import Millisecond


@export
@dataclass(frozen=True)
class TransitionConfig:
    """
    Configuration class for transition scenes.

    This config is used by `nextrpg.scene.transition_scene.TransitionScene`.

    Arguments:
        `duration`: The total duration of the transition
            in milliseconds.
    """

    duration: Millisecond = 500
