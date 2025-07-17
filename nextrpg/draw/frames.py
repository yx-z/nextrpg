"""
Frame-based animation system for `nextrpg`.

This module provides a frame-based animation system that allows static drawings
to be played sequentially to create animated effects. It includes the
`CyclicFrames` class for managing frame sequences with configurable timing.

Features:
    - Sequential frame playback with timing control
    - Cyclic animation loops
    - Configurable frame duration
    - Timer-based frame advancement
    - Animation state management
"""

from dataclasses import KW_ONLY, replace
from typing import Self

from nextrpg.core.time import Millisecond, Timer
from nextrpg.draw.draw_on_screen import Drawing
from nextrpg.core.model import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)


@dataclass_with_instance_init
class CyclicFrames:
    """
    Static frames that can be played sequentially to create animations.

    This class manages a sequence of static drawings that are displayed in order
    to create animated effects. It handles timing, frame advancement, and cyclic
    looping of the animation sequence.

    Arguments:
        frames: Tuple of drawings that make up the animation sequence.
        duration_per_frame: Time to display each frame in milliseconds.
        _index: Current frame index in the sequence.
        _timer: Internal timer for frame timing control.
    """

    frames: tuple[Drawing, ...]
    duration_per_frame: Millisecond
    _: KW_ONLY = not_constructor_below()
    _index: int = 0
    _timer: Timer = instance_init(lambda self: Timer(self.duration_per_frame))

    @property
    def current_frame(self) -> Drawing:
        """
        Get the currently active frame in the animation sequence.

        Returns the drawing at the current animation index position. The result
        is cached until the instance is replaced with a new one.

        Returns:
            The current frame in the animation sequence.
        """
        return self.frames[self._index]

    def tick(self, time_delta: Millisecond) -> Self:
        """
        Advance animation frames based on elapsed time.

        Calculates how many frames to advance based on the accumulated time and
        creates a new `CyclicFrames` instance with updated index and elapsed
        time.

        Arguments:
            time_delta: The time that has passed since the last step.

        Returns:
            A new instance with an updated animation state.
        """
        timer = self._timer.tick(time_delta)
        frames_to_step = timer.elapsed // self.duration_per_frame
        index = (self._index + frames_to_step) % len(self.frames)
        timer_mod = replace(
            timer, elapsed=timer.elapsed % self.duration_per_frame
        )
        return replace(self, _index=index, _timer=timer_mod)

    @property
    def reset(self) -> Self:
        """
        Reset the animation sequence to its initial state.

        Creates a new `CyclicFrames` instance with the animation index and
        elapsed time reset to zero, effectively restarting the animation.

        Returns:
            A new instance with the animation state reset to the beginning of
            the sequence.
        """
        return replace(self, _index=0, _timer=self._timer.reset)
