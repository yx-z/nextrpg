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
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import Self, TypeIs, override

from nextrpg.core.dataclass_with_instance_init import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond, Timer
from nextrpg.draw.animated_on_screen import AnimatedOnScreen
from nextrpg.draw.color import alpha_from_percentage
from nextrpg.draw.draw import DrawOnScreen
from nextrpg.global_config.global_config import config


@dataclass_with_instance_init(frozen=True)
class Fade(AnimatedOnScreen, ABC):
    """
    Fade effect for transitioning drawing resources.

    This class provides fade effect functionality that gradually changes the
    alpha transparency of drawing resources over time. It's commonly used for
    scene transitions and visual effects.

    Arguments:
        resource: The drawing resources to fade.
        duration: The duration of the fade effect in milliseconds. Defaults to
            the global transition duration.
    """

    resource: (
        DrawOnScreen
        | tuple[DrawOnScreen, ...]
        | AnimatedOnScreen
        | tuple[AnimatedOnScreen, ...]
    )
    duration: Millisecond = field(
        default_factory=lambda: config().transition.duration
    )
    _: KW_ONLY = not_constructor_below()
    _timer: Timer = instance_init(lambda self: Timer(self.duration))

    @cached_property
    @override
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
        if self._timer.complete:
            return self._complete
        if self._timer.elapsed == 0:
            return self._start

        alpha = alpha_from_percentage(self._percentage)
        return tuple(d.set_alpha(alpha) for d in self._draw_on_screens)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        timer = self._timer.tick(time_delta)
        if isinstance(self.resource, AnimatedOnScreen):
            return replace(
                self, resource=self.resource.tick(time_delta), _timer=timer
            )
        if _is_animated_tuple(self.resource):
            animations = tuple(a.tick(time_delta) for a in self.resource)
            return replace(self, resource=animations, _timer=timer)
        return replace(self, _timer=timer)

    @property
    def complete(self) -> bool:
        """
        Check if the fade effect has completed.

        Returns:
            Whether the fade effect has finished.
        """
        return self._timer.complete

    @cached_property
    def _draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        if isinstance(self.resource, DrawOnScreen):
            return (self.resource,)
        if isinstance(self.resource, AnimatedOnScreen):
            return self.resource.draw_on_screens
        if _is_animated_tuple(self.resource):
            return tuple(d for a in self.resource for d in a.draw_on_screens)
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
        return self._draw_on_screens

    @override
    @property
    def _percentage(self) -> float:
        return self._timer.completed_percentage


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
        return self._timer.remaining_percentage

    @override
    @property
    def _start(self) -> tuple[DrawOnScreen, ...]:
        return self._draw_on_screens

    @override
    @property
    def _complete(self) -> tuple[DrawOnScreen, ...]:
        return ()


def _is_animated_tuple(
    resource: (
        DrawOnScreen
        | tuple[DrawOnScreen, ...]
        | AnimatedOnScreen
        | tuple[AnimatedOnScreen, ...]
    ),
) -> TypeIs[tuple[AnimatedOnScreen, ...]]:
    if not resource:
        return False
    if not isinstance(resource, tuple):
        return False
    if not isinstance(resource[0], AnimatedOnScreen):
        return False
    return True
