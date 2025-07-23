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
from typing import Self, override

from nextrpg.core.dataclass_with_instance_init import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond, Timer
from nextrpg.draw.animated import Animated
from nextrpg.draw.draw_on_screen import Drawing


@dataclass_with_instance_init
class CyclicFrames(Animated):
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
    @override
    def drawings(self) -> tuple[Drawing, ...]:
        return (self.drawing,)

    @property
    def drawing(self) -> Drawing:
        return self.frames[self._index]

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        timer = self._timer.tick(time_delta)
        frames_to_step = timer.elapsed // self.duration_per_frame
        index = (self._index + frames_to_step) % len(self.frames)
        return replace(self, _index=index, _timer=timer.modulo)

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
