from dataclasses import dataclass

from nextrpg.core import Millisecond


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
