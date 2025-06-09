"""
Static frames, when played sequentially, become animated.
"""

from enum import Enum, auto
from typing import Final

from nextrpg.draw_on_screen import Drawing

type FrameIndex = int
"""The zero-based index to point to a frame in a list of frames."""


class FrameExhaustedOption(Enum):
    """
    Options for handling scenarios where frames are all played once/exhausted.

    Attributes:
        `CYCLE`: Cycles back to the first frame when frames are exhausted.

        `KEEP_LAST_FRAME`: Maintains the last frame once all frames are used.

        `DISAPPEAR`: Makes the sprite disappear when no frames are left.
    """

    CYCLE = auto()
    KEEP_LAST_FRAME = auto()
    DISAPPEAR = auto()


class Frames:
    """
    This class holds A collection of frames to be iterated,
    and the behavior upon frame exhaustion.
    """

    def __init__(
        self,
        frames: list[Drawing],
        frame_exhausted_option: FrameExhaustedOption,
        frame_indices: list[FrameIndex] | None = None,
    ) -> None:
        """
        Initializes the object with frames, options for handling
        frame exhaustion, and optionally sequence of specific frame indices.

        Args:
            `frames`:
                A list of Drawing objects representing the frames to work with.

            `frame_exhausted_option`:
                Defines the behavior to apply when frames have been exhausted.

            `frame_indices`:
                An optional list of `FrameIndex` specifying a sequence of frame
                indices to consume. If not provided, the full range of frames
                will be played sequentially.

                For example, if `frame_indices == [2, 0, 1]`.
                `frames[2]` will be played first, followed by `frames[0]` and
                `frames[1]`.
        """
        self._frames: Final[list[Drawing]] = frames
        self._frame_exhausted_option: Final[FrameExhaustedOption] = (
            frame_exhausted_option
        )
        self._frame_indices: Final[list[FrameIndex]] = frame_indices or list(
            range(len(frames))
        )
        self._frame_indices_index: int | None = 0

    def reset(self) -> None:
        """
        Resets the frame index to the beginning.

        Args:
            `None`

        Returns:
            `None`
        """
        self._frame_indices_index = 0

    def current_frame(self) -> Drawing | None:
        """
        Returns the currently selected frame, if applicable.

        If the current frame index exists, the method retrieves the frame at the
        corresponding position in the sequence. None if no index is set.

        Returns:
            `Drawing | None`: The current frame if a valid index is set, or None
                if no frame is selected.
        """
        return (
            self._frames[self._frame_indices[self._frame_indices_index]]
            if self._frame_indices_index is not None
            else None
        )

    def next_frame(self) -> Drawing | None:
        """
        Advances to the next frame in sequence and returns the current frame.

        This method triggers the frame exhaustion behavior
        if there are no more frames.
        It will either cycle the frames, keep the last frame, or disappear.

        Returns:
            `Drawing | None`: The frame after updating the frame index. If the
                frames are exhausted and the option is set to disappear,
                `None` is returned.
        """
        if self._frame_indices_index is not None:
            self._frame_indices_index += 1
        if self._frame_indices_index == len(self._frame_indices):
            self._frame_indices_index = {
                FrameExhaustedOption.CYCLE: 0,
                FrameExhaustedOption.KEEP_LAST_FRAME: len(self._frames) - 1,
                FrameExhaustedOption.DISAPPEAR: None,
            }[self._frame_exhausted_option]
        return self.current_frame()
