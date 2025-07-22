from dataclasses import KW_ONLY, dataclass, replace
from typing import Self

from pygame.time import get_ticks

from nextrpg.core.model import not_constructor_below

type Millisecond = int
"""
Millisecond elapsed between game loops.
"""


@dataclass(frozen=True)
class Timer:
    """
    A timer with duration and elapsed time tracking.

    This class provides a simple timer mechanism for tracking elapsed
    time and determining when a timer has completed. It's commonly
    used for animations, delays, and time-based game mechanics.

    Arguments:
        `duration`: The total duration of the timer in milliseconds.

        `elapsed`: The elapsed time in milliseconds. Defaults to 0.

    Example:
        ```python
        # Create a 2-second timer
        timer = Timer(2000)

        # Update timer in game loop
        timer = timer.tick(time_delta)

        # Check if timer is complete
        if timer.complete:
            print("Timer finished!")
        ```
    """

    duration: Millisecond
    _: KW_ONLY = not_constructor_below()
    elapsed: Millisecond = 0

    @property
    def modulo(self) -> Self:
        return self.reset.tick(self.elapsed % self.duration)

    def tick(self, time_delta: Millisecond) -> Self:
        """
        Tick the timer in a game loop.

        Advances the timer by the given time delta and returns a new
        timer instance with updated elapsed time.

        Arguments:
            `time_delta`: The time elapsed since the last tick in
                milliseconds.

        Returns:
            `Timer`: A new timer with elapsed time updated.

        Example:
            ```python
            timer = Timer(1000)  # 1 second timer
            timer = timer.tick(100)  # Advance by 100ms
            ```
        """
        return replace(self, elapsed=self.elapsed + time_delta)

    @property
    def reset(self) -> Self:
        """
        Get a reset timer.

        Creates a new timer instance with the same duration but
        elapsed time set to 0.

        Returns:
            `Timer`: A new timer with elapsed time set to 0.

        Example:
            ```python
            timer = Timer(1000, 500)  # 1s timer, 500ms elapsed
            reset_timer = timer.reset  # 1s timer, 0ms elapsed
            ```
        """
        return replace(self, elapsed=0)

    @property
    def complete(self) -> bool:
        """
        Get whether the timer has completed.

        Returns:
            `bool`: Whether the timer has completed (elapsed >= duration).

        Example:
            ```python
            timer = Timer(1000, 1200)  # 1s timer, 1.2s elapsed
            if timer.complete:
                print("Timer is done!")
            ```
        """
        return self.elapsed > self.duration

    @property
    def completed_percentage(self) -> float:
        return self.elapsed / self.duration

    @property
    def remaining(self) -> Millisecond:
        return self.duration - self.elapsed

    @property
    def remaining_percentage(self) -> float:
        return self.remaining / self.duration


def get_timepoint() -> Millisecond:
    """
    Get the current time point in milliseconds.

    Returns the current time from pygame's clock, which is typically
    used for calculating time deltas in game loops.

    Returns:
        `Millisecond`: Current time in milliseconds.

    Example:
        ```python
        start_time = get_timepoint()
        # ... do some work ...
        end_time = get_timepoint()
        elapsed = end_time - start_time
        ```
    """
    return get_ticks()
