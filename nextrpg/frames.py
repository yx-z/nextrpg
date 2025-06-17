"""
Static frames, when played sequentially, become animated.
"""

from dataclasses import dataclass, replace
from functools import cached_property

from nextrpg.common_types import Millisecond
from nextrpg.draw_on_screen import Drawing

type _FrameIndex = int


@dataclass(frozen=True)
class CyclicFrames:
    """
    Static frames that can be played sequentially to create animations.

    Args:
        `frames`: List of drawings that make up the animation sequence.

        `duration_per_frame`: Time to display each frame in milliseconds.

    Returns:
        `CyclicFrames`: An instance managing a frame-based animation sequence.
    """

    frames: list[Drawing]
    duration_per_frame: Millisecond
    _index: _FrameIndex = 0
    _elapsed: Millisecond = 0

    @cached_property
    def current_frame(self) -> Drawing:
        """
        Get the currently active frame in the animation sequence.

        Returns the drawing at the current animation index position.
        The result is cached until the instance is replaced with a new one.

        Returns:
            `Drawing`: The current frame in the animation sequence.
        """
        return self.frames[self._index]

    def step(self, time_delta: Millisecond) -> "CyclicFrames":
        """
        Advance animation frames based on elapsed time.

        Calculates how many frames to advance based on the accumulated time and
        creates a new CyclicFrames instance with updated index and elapsed time.

        Args:
            `time_delta`: The time that has passed since the last step.

        Returns:
            `CyclicFrames`: A new instance with an updated animation state.
            The frame index is updated according to elapsed time and
            wraps around when it reaches the end of the frame list.
        """
        total_time = self._elapsed + time_delta
        frames_to_step = total_time // self.duration_per_frame
        return replace(
            self,
            _index=(self._index + frames_to_step) % len(self.frames),
            _elapsed=total_time % self.duration_per_frame,
        )

    def reset(self) -> "CyclicFrames":
        """
        Reset the animation sequence to its initial state.

        Creates a new CyclicFrames instance with the animation index and
        elapsed time reset to zero, effectively restarting the animation.

        Returns:
            `CyclicFrames`: A new instance with the animation state reset to
            the beginning of the sequence.
        """
        return replace(self, _index=0, _elapsed=0)
