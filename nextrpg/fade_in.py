"""
Fade-in effect system for `nextrpg`.

This module provides fade-in effect functionality for transitions in `nextrpg`
games. It includes the `FadeIn` class which handles gradual appearance of
drawing resources over time.

Features:
    - Gradual alpha increase over time
    - Configurable fade duration
    - Resource alpha manipulation
    - Integration with fade system
"""

from functools import cached_property
from typing import override

from nextrpg.draw_on_screen import DrawOnScreen
from nextrpg.fade import Fade
from nextrpg.model import dataclass_with_instance_init, export, instance_init


@export
@dataclass_with_instance_init
class FadeIn(Fade):
    """
    Fade-in effect for gradually appearing drawing resources.

    This class provides fade-in effect functionality that gradually increases
    the alpha transparency of drawing resources over time, making them appear
    from transparent to fully opaque.

    Arguments:
        _complete: The final drawing state (fully opaque resources).
            Automatically initialized to the input resources.
    """

    _complete: tuple[DrawOnScreen] = instance_init(lambda self: self.resource)

    @override
    @cached_property
    def _start(self) -> tuple[DrawOnScreen, ...]:
        """
        Get the initial drawing state (empty).

        Returns:
            Empty drawing tuple.
        """
        return ()

    @override
    @cached_property
    def _percentage(self) -> float:
        """
        Get the fade-in completion percentage.

        Calculates the percentage based on elapsed time divided by total
        duration.

        Returns:
            The fade-in completion percentage (0.0 to 1.0).
        """
        return self._elapsed / self.duration
