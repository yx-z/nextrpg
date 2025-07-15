"""
Transition configuration system for NextRPG.

This module provides configuration options for scene transitions
in NextRPG games. It includes the `TransitionConfig` class which
defines timing parameters for smooth scene transitions.

The transition configuration features:
- Configurable transition duration
- Integration with transition scene system
- Timing control for smooth animations

Example:
    ```python
    from nextrpg.transition_config import TransitionConfig
    from nextrpg.core import Millisecond

    # Create default transition config
    config = TransitionConfig()

    # Create custom transition config
    custom_config = TransitionConfig(duration=Millisecond(1000))
    ```
"""

from dataclasses import dataclass

from nextrpg.core import Millisecond
from nextrpg.model import export


@export
@dataclass(frozen=True)
class TransitionConfig:
    """
    Configuration class for transition scenes.

    This config is used by `nextrpg.scene.transition_scene.TransitionScene`
    to control the timing and behavior of scene transitions.

    Arguments:
        `duration`: The total duration of the transition
            in milliseconds. Defaults to 500ms.

    Example:
        ```python
        from nextrpg.transition_config import TransitionConfig
        from nextrpg.core import Millisecond

        # Default transition (500ms)
        config = TransitionConfig()

        # Slow transition (2 seconds)
        slow_config = TransitionConfig(duration=Millisecond(2000))

        # Fast transition (100ms)
        fast_config = TransitionConfig(duration=Millisecond(100))
        ```
    """

    duration: Millisecond = 500
