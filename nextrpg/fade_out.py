"""
Fade-out effect system for NextRPG.

This module provides fade-out effect functionality for transitions
in NextRPG games. It includes the `FadeOut` class which handles
gradual disappearance of drawing resources over time.

The fade-out effect system features:
- Gradual alpha decrease over time
- Configurable fade duration
- Resource alpha manipulation
- Integration with fade system

Example:
    ```python
    from nextrpg.fade_out import FadeOut
    from nextrpg.draw_on_screen import DrawOnScreen
    from nextrpg.core import Millisecond

    # Create fade-out effect
    fade_out = FadeOut(resource=drawings, duration=Millisecond(1000))

    # Update fade-out in game loop
    fade_out = fade_out.tick(time_delta)
    ```
"""

from functools import cached_property
from typing import override

from nextrpg.draw_on_screen import DrawOnScreen
from nextrpg.fade import Fade
from nextrpg.model import dataclass_with_instance_init, export, instance_init


@export
@dataclass_with_instance_init
class FadeOut(Fade):
    """
    Fade-out effect for gradually disappearing drawing resources.

    This class provides fade-out effect functionality that gradually
    decreases the alpha transparency of drawing resources over time,
    making them disappear from fully opaque to transparent.

    Arguments:
        `_start`: The initial drawing state (fully opaque resources).
            Automatically initialized to the input resources.

    Example:
        ```python
        from nextrpg.fade_out import FadeOut
        from nextrpg.draw_on_screen import DrawOnScreen
        from nextrpg.core import Millisecond

        # Create fade-out effect
        fade_out = FadeOut(resource=drawings, duration=Millisecond(2000))

        # Update in game loop
        fade_out = fade_out.tick(time_delta)

        # Check if complete
        if fade_out.complete:
            # Handle completion
            pass
        ```
    """

    _start: tuple[DrawOnScreen, ...] = instance_init(lambda self: self.resource)

    @override
    @cached_property
    def _percentage(self) -> float:
        """
        Get the fade-out completion percentage.

        Calculates the percentage based on remaining time divided
        by total duration, so it decreases from 1.0 to 0.0.

        Returns:
            `float`: The fade-out completion percentage (1.0 to 0.0).
        """
        remaining = self.duration - self._elapsed
        return remaining / self.duration

    @override
    @cached_property
    def _complete(self) -> tuple[DrawOnScreen, ...]:
        """
        Get the final drawing state (empty).

        Returns:
            `tuple[DrawOnScreen, ...]`: Empty drawing tuple.
        """
        return ()
