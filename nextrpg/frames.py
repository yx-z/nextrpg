"""
Frame-based animation system for NextRPG.

This module provides a frame-based animation system that allows
static drawings to be played sequentially to create animated
effects. It includes the `CyclicFrames` class for managing
frame sequences with configurable timing.

The animation system features:
- Sequential frame playback with timing control
- Cyclic animation loops
- Configurable frame duration
- Timer-based frame advancement
- Animation state management

Example:
    ```python
    from nextrpg.frames import CyclicFrames
    from nextrpg.draw_on_screen import Drawing

    # Create frame sequence
    frames = (frame1, frame2, frame3, frame4)
    animation = CyclicFrames(frames=frames, duration_per_frame=100)

    # Update animation in game loop
    animation = animation.tick(time_delta)

    # Get current frame
    current_frame = animation.current_frame
    ```
"""

from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import Self

from nextrpg.core import Millisecond, Timer
from nextrpg.draw_on_screen import Drawing
from nextrpg.model import (
    dataclass_with_instance_init,
    export,
    instance_init,
    not_constructor_below,
)


@export
@dataclass_with_instance_init
class CyclicFrames:
    """
    Static frames that can be played sequentially to create animations.

    This class manages a sequence of static drawings that are displayed
    in order to create animated effects. It handles timing, frame
    advancement, and cyclic looping of the animation sequence.

    Arguments:
        `frames`: Tuple of drawings that make up the animation sequence.

        `duration_per_frame`: Time to display each frame in milliseconds.

        `_index`: Current frame index in the sequence.

        `_timer`: Internal timer for frame timing control.

    Example:
        ```python
        from nextrpg.frames import CyclicFrames
        from nextrpg.draw_on_screen import Drawing

        # Create animation from sprite frames
        frames = (sprite_frame1, sprite_frame2, sprite_frame3)
        animation = CyclicFrames(frames=frames, duration_per_frame=150)

        # Update in game loop
        animation = animation.tick(time_delta)

        # Get current frame for rendering
        current_frame = animation.current_frame
        ```
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

        Returns the drawing at the current animation index position.
        The result is cached until the instance is replaced with a new one.

        Returns:
            `Drawing`: The current frame in the animation sequence.

        Example:
            ```python
            # Get current frame for rendering
            current_frame = animation.current_frame
            ```
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

        Example:
            ```python
            # Update animation in game loop
            animation = animation.tick(time_delta)
            ```
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

        Example:
            ```python
            # Reset animation to beginning
            animation = animation.reset
            ```
        """
        return replace(self, _index=0, _timer=self._timer.reset)
