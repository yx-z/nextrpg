"""
Static frames, when played sequentially, become animated.
"""

from dataclasses import replace
from functools import cached_property
from typing import Self

from nextrpg.core import Millisecond, Timer
from nextrpg.draw.draw_on_screen import Drawing
from nextrpg.model import instance_init, dataclass_with_instance_init


@dataclass_with_instance_init
class CyclicFrames:
    """
    Static frames that can be played sequentially to create animations.

    Arguments:
        `frames`: Tuple of drawings that make up the animation sequence.

        `duration_per_frame`: Time to display each frame in milliseconds.

    Returns:
        `CyclicFrames`: An instance managing a frame-based animation sequence.
    """

    frames: tuple[Drawing, ...]
    duration_per_frame: Millisecond
    _index: int = 0
    _timer: Timer = instance_init(lambda self: Timer(self.duration_per_frame))

    @property
    def current_frame(self) -> Drawing:
        """
        Get the currently active frame in the animation sequence.

        Returns the drawing at the current animation index position.
        The result is cached until the instance is replaced with a new one.

        Returns:
            `Drawing`: The current frame in the animation sequence.
        """
        return self.frames[self._index]

    def tick(self, time_delta: Millisecond) -> Self:
        """
        Advance animation frames based on elapsed time.

        Calculates how many frames to advance based on the accumulated time and
        creates a new CyclicFrames instance with updated index and elapsed time.

        Arguments:
            `time_delta`: The time that has passed since the last step.

        Returns:
            `CyclicFrames`: A new instance with an updated animation state.
        """
        timer = self._timer.tick(time_delta)
        frames_to_step = timer.elapsed // self.duration_per_frame
        index = (self._index + frames_to_step) % len(self.frames)
        timer_mod = replace(
            timer, elapsed=timer.elapsed % self.duration_per_frame
        )
        return replace(self, _index=index, _timer=timer_mod)

    @cached_property
    def reset(self) -> Self:
        """
        Reset the animation sequence to its initial state.

        Creates a new CyclicFrames instance with the animation index and
        elapsed time reset to zero, effectively restarting the animation.

        Returns:
            `CyclicFrames`: A new instance with the animation state reset to
            the beginning of the sequence.
        """
        return replace(self, _index=0, _timer=self._timer.reset)
