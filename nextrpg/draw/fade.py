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

from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass, field, replace
from typing import Self, override

from nextrpg.core.model import not_constructor_below
from nextrpg.core.time import Millisecond
from nextrpg.draw.color import alpha_from_percentage
from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.global_config.global_config import config


@dataclass(frozen=True)
class Fade(ABC):
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

    resource: DrawOnScreen | tuple[DrawOnScreen, ...]
    duration: Millisecond = field(
        default_factory=lambda: config().transition.duration
    )
    _: KW_ONLY = not_constructor_below()
    _elapsed: Millisecond = 0

    @property
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
        return self._resource_tuple

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
        if isinstance(self.resource, DrawOnScreen):
            resource = self.resource.set_alpha(alpha)
        else:
            resource = tuple(d.set_alpha(alpha) for d in self.resource)
        return replace(self, _elapsed=elapsed, resource=resource)

    @property
    def complete(self) -> bool:
        """
        Check if the fade effect has completed.

        Returns:
            Whether the fade effect has finished.
        """
        return self._elapsed >= self.duration

    @property
    def _resource_tuple(self) -> tuple[DrawOnScreen, ...]:
        if isinstance(self.resource, DrawOnScreen):
            return (self.resource,)
        return self.resource

    @property
    @abstractmethod
    def _start(self) -> tuple[DrawOnScreen, ...]:
        """
        Get the initial drawing state (empty).

        Returns:
            Empty drawing tuple.
        """

    @property
    @abstractmethod
    def _complete(self) -> tuple[DrawOnScreen, ...]:
        """
        Get the final drawing state (empty).

        Returns:
            Empty drawing tuple.
        """

    @property
    @abstractmethod
    def _percentage(self) -> float:
        """
        Get the fade completion percentage.

        Returns:
            The fade completion percentage (0.0 to 1.0).
        """


class FadeIn(Fade):
    """
    Fade-in effect for gradually appearing drawing resources.

    This class provides fade-in effect functionality that gradually increases
    the alpha transparency of drawing resources over time, making them appear
    from transparent to fully opaque.
    """

    @override
    @property
    def _start(self) -> tuple[DrawOnScreen, ...]:
        return ()

    @override
    @property
    def _complete(self) -> tuple[DrawOnScreen, ...]:
        return self._resource_tuple

    @override
    @property
    def _percentage(self) -> float:
        return self._elapsed / self.duration


class FadeOut(Fade):
    """
    Fade-out effect for gradually disappearing drawing resources.

    This class provides fade-out effect functionality that gradually decreases
    the alpha transparency of drawing resources over time, making them disappear
    from fully opaque to transparent.
    """

    @override
    @property
    def _percentage(self) -> float:
        remaining = self.duration - self._elapsed
        return remaining / self.duration

    @override
    @property
    def _start(self) -> tuple[DrawOnScreen, ...]:
        return self._resource_tuple

    @override
    @property
    def _complete(self) -> tuple[DrawOnScreen, ...]:
        return ()
