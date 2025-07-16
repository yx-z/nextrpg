"""
Fade effect system for `nextrpg`.

This module provides fade effect functionality for transitions in `nextrpg`
games. It includes the `Fade` class which handles alpha-based fading of
drawing resources over time.

Features:
    - Time-based alpha transitions
    - Configurable fade duration
    - Resource alpha manipulation
    - Integration with transition system
"""

from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Self

from nextrpg.core import Millisecond, alpha_from_percentage
from nextrpg.draw_on_screen import DrawOnScreen
from nextrpg.global_config import config
from nextrpg.model import export


@export
@dataclass(frozen=True)
class Fade:
    """
    Fade effect for transitioning drawing resources.

    This class provides fade effect functionality that gradually changes the
    alpha transparency of drawing resources over time. It's commonly used for
    scene transitions and visual effects.

    Arguments:
        resource: The drawing resources to fade.
        duration: The duration of the fade effect in milliseconds. Defaults to
            the global transition duration.
        _elapsed: Internal elapsed time tracking.
    """

    resource: tuple[DrawOnScreen, ...]
    duration: Millisecond = field(
        default_factory=lambda: config().transition.duration
    )
    _elapsed: Millisecond = 0

    @cached_property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        """
        Get the current drawing resources for rendering.

        Returns different drawing sets based on the fade state:
        - Empty at start
        - Faded resources during transition
        - Empty at completion

        Returns:
            The current drawing resources.
        """
        if self.complete:
            return self._complete
        if self._elapsed == 0:
            return self._start
        return self.resource

    def tick(self, time_delta: Millisecond) -> Self:
        """
        Update the fade effect based on elapsed time.

        Advances the fade effect and updates the alpha values of the drawing
        resources based on the elapsed time.

        Arguments:
            time_delta: The elapsed time in milliseconds.

        Returns:
            A new fade instance with updated state.
        """
        if self.complete:
            return self
        elapsed = self._elapsed + time_delta
        alpha = alpha_from_percentage(self._percentage)
        resource = tuple(d.set_alpha(alpha) for d in self.resource)
        return replace(self, _elapsed=elapsed, resource=resource)

    @cached_property
    def complete(self) -> bool:
        """
        Check if the fade effect has completed.

        Returns:
            Whether the fade effect has finished.
        """
        return self._elapsed >= self.duration

    @cached_property
    def _start(self) -> tuple[DrawOnScreen, ...]:
        """
        Get the initial drawing state (empty).

        Returns:
            Empty drawing tuple.
        """
        return ()

    @cached_property
    def _complete(self) -> tuple[DrawOnScreen, ...]:
        """
        Get the final drawing state (empty).

        Returns:
            Empty drawing tuple.
        """
        return ()

    @cached_property
    def _percentage(self) -> float:
        """
        Get the fade completion percentage.

        Returns:
            The fade completion percentage (0.0 to 1.0).
        """
        return 0
