"""
Transition configuration system for `NextRPG`.

This module provides configuration options for scene transitions in `NextRPG`
games. It includes the `TransitionConfig` class which defines timing parameters
for smooth scene transitions.

The transition configuration features:
- Configurable transition duration
- Integration with transition scene system
- Timing control for smooth animations
"""

from dataclasses import dataclass

from nextrpg.core.time import Millisecond


@dataclass(frozen=True)
class TransitionConfig:
    """
    Configuration class for transition scenes.

    This global_config is used by `nextrpg.scene.transition_scene.TransitionScene` to
    control the timing and behavior of scene transitions.

    Arguments:
        `duration`: The total duration of the transition in milliseconds.
            Defaults to 500ms.
    """

    duration: Millisecond = 500
