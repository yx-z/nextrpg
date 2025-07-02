"""
RPG Maker character drawing implementation.

This module provides functionality for rendering RPG Maker-style character
drawing with support for different sprite sheet formats and animation patterns.

Note that `nextrpg` is only compatible with the
RPG Maker character sprite sheet to be able to re-use existing resources.

However, using RPG Maker's
[Runtime Time Package (RTP)](https://www.rpgmakerweb.com/run-time-package)
in non-RPG Maker framework violates the license of RPG Maker,
even if you own a copy of RPG Maker.
"""

from dataclasses import dataclass, field, replace
from enum import IntEnum
from typing import override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.config import config
from nextrpg.core import Direction, Millisecond, Pixel
from nextrpg.draw_on_screen import Coordinate, Drawing, Size
from nextrpg.frames import CyclicFrames
from nextrpg.model import instance_init, register_instance_init

type _FrameIndices = list[int]


class DefaultFrameType(IntEnum):
    """
    RPG Maker VX/VX Ace/MV/MZ sprite sheet format (4 direction x 3 frames).
    """

    _RIGHT_FOOT = 0
    _IDLE = 1
    _LEFT_FOOT = 2

    @classmethod
    def _frame_indices(cls) -> _FrameIndices:
        return [
            DefaultFrameType._IDLE,
            DefaultFrameType._RIGHT_FOOT,
            DefaultFrameType._IDLE,
            DefaultFrameType._LEFT_FOOT,
        ]


class XpFrameType(IntEnum):
    """
    RPG Maker XP sprite sheet format (4 direction x 4 frames).
    """

    _IDLE = 0
    _RIGHT_FOOT = 1
    _IDLE_AGAIN = 2
    _LEFT_FOOT = 3

    @classmethod
    def _frame_indices(cls) -> _FrameIndices:
        return list(cls)


type FrameType = type[DefaultFrameType | XpFrameType]
"""Choose between DefaultFrameType and XpFrameType."""


@dataclass(frozen=True)
class SpriteSheetSelection:
    """
    Zero-indexed row/column for selecting a portion of a sprite sheet.

    Defines the position and boundaries for extracting a specific character
    sprite sheet from a larger sprite sheet containing multiple characters.

    Arguments:
        `row`: Row index of the character in the sprite sheet.

        `column`: Column index of the character in the sprite sheet.

        `max_rows`: Total number of rows in the sprite sheet.
            Default to two rows.

        `max_columns`: Total number of columns in the sprite sheet.
            Default to four columns.
    """

    row: int
    column: int
    max_rows: int = 2
    max_columns: int = 4


@dataclass(frozen=True)
class Margin:
    """
    Margin of a single character frame to crop from the sprite sheet.
    """

    top: Pixel = 0
    left: Pixel = 0
    bottom: Pixel = 0
    right: Pixel = 0


@dataclass(frozen=True)
class SpriteSheet:
    """
    Container for sprite sheet configuration.

    Holds all necessary information to process and render character
    from a sprite sheet image.

    Arguments:
        `drawing`: The sprite sheet image to process.

        `selection`: Optional for selecting a portion of the sprite sheet.

        `style`: The sprite sheet format style to use.
    """

    drawing: Drawing
    selection: SpriteSheetSelection | None = None
    style: FrameType = DefaultFrameType
    margin: Margin = Margin()


def _init_frames(
    self: RpgMakerCharacterDrawing,
) -> dict[Direction, CyclicFrames]:
    drawing = (
        self._crop_by_selection(select)
        if (select := self.sprite_sheet.selection)
        else self.sprite_sheet.drawing
    )
    return {
        direction: self._load_frames_row(drawing, row)
        for direction, row in _DIR_TO_ROW.items()
    }


@register_instance_init
class RpgMakerCharacterDrawing(CharacterDrawing):
    """
    RPG Maker style character drawing.

    Arguments:
        `sprite_sheet`: Configuration for the character's sprite sheet.

        `animate_on_idle`: Whether to animate the character when not moving.

        `frame_duration`: Duration for each animation frame in milliseconds.
            If not specified, the default duration from `Config` is used.

        `initial_direction`: Initial direction for the character.
            If not specified, the default direction from `Config` is used.
    """

    sprite_sheet: SpriteSheet
    animate_on_idle: bool = False
    frame_duration: Millisecond = field(
        default_factory=lambda: config().rpg_maker_character.frame_duration
    )
    _frames: dict[Direction, CyclicFrames] = instance_init(_init_frames)

    @property
    def drawing(self) -> Drawing:
        """
        Get the current visual representation of the character.

        Retrieves the current animation frame for the character's current
        direction, adjusting diagonal directions to their closest cardinal
        direction.

        Returns:
            `Drawing`: The current frame of the character's sprite animation.
        """
        return self._frames[_adjust(self.direction)].current_frame

    @override
    def turn(self, direction: Direction) -> CharacterDrawing:
        """
        Change the character's facing direction.

        Creates a new character drawing with the specified direction and resets
        animation frames for all directions except the new one.

        Arguments:
            `direction`: The new direction for the character to face.

        Returns:
            `CharacterDrawing`: A new character drawing instance facing the
            specified direction.
        """
        return replace(
            self,
            direction=direction,
            _frames={
                d: frames if d == _adjust(direction) else frames.reset()
                for d, frames in self._frames.items()
            },
        )

    @override
    def move(self, time_delta: Millisecond) -> CharacterDrawing:
        """
        Update the character's movement animation over the given time delta.

        Advances the animation frames for the current direction while leaving
        other direction frames unchanged.

        Arguments:
            `time_delta`: The amount of time that has
                passed since the last update.

        Returns:
            `CharacterDrawing`: The updated drawing with a new animation state
            for the current direction.
        """
        return replace(
            self,
            _frames={
                direction: self._move_frame(time_delta, direction)
                for direction, frames in self._frames.items()
            },
        )

    def _move_frame(
        self, time_delta: Millisecond, adjusted_direction: Direction
    ) -> CyclicFrames:
        frames = self._frames[adjusted_direction]
        return (
            frames.tick(time_delta)
            if adjusted_direction == _adjust(self.direction)
            else frames
        )

    @override
    def idle(self, time_delta: Millisecond) -> CharacterDrawing:
        """
        Update the character's idle animation state over the given time delta.

        If animate_on_idle is enabled, continues cycling through animation
        frames even when idle.
        Otherwise, resets all frames to their initial state.

        Arguments:
            `time_delta`: The amount of time that has passed
                since the last update.

        Returns:
            `CharacterDrawing`: The updated drawing
            with a new idle animation state.
        """
        if self.animate_on_idle:
            return self.move(time_delta)
        return replace(
            self,
            _frames={d: frames.reset() for d, frames in self._frames.items()},
        )

    def _crop_by_selection(self, selection: SpriteSheetSelection) -> Drawing:
        drawing = self.sprite_sheet.drawing
        width = drawing.width / selection.max_columns
        height = drawing.height / selection.max_rows
        return drawing.crop(
            Coordinate(width * selection.column, height * selection.row),
            Size(width, height),
        )

    def _load_frames_row(self, drawing: Drawing, row: int) -> CyclicFrames:
        frames = [
            self._crop_margin(d)
            for d in self._crop_into_frames_at_row(drawing, row)
        ]
        return CyclicFrames(
            [frames[i] for i in self.sprite_sheet.style._frame_indices()],
            self.frame_duration,
        )

    def _crop_into_frames_at_row(
        self, drawing: Drawing, row: int
    ) -> list[Drawing]:
        num_frames = len(self.sprite_sheet.style)
        width = drawing.width / num_frames
        height = drawing.height / 4
        return [
            drawing.crop(
                Coordinate(width * i, height * row), Size(width, height)
            )
            for i in range(num_frames)
        ]

    def _crop_margin(self, drawing: Drawing) -> Drawing:
        margin = self.sprite_sheet.margin
        return drawing.crop(
            Coordinate(margin.left, margin.top),
            Size(
                drawing.width - margin.left - margin.right,
                drawing.height - margin.top - margin.bottom,
            ),
        )


_DIR_TO_ROW = {
    Direction.DOWN: 0,
    Direction.LEFT: 1,
    Direction.RIGHT: 2,
    Direction.UP: 3,
}


_EIGHT_TO_FOUR = {
    Direction.RIGHT: Direction.RIGHT,
    Direction.LEFT: Direction.LEFT,
    Direction.UP: Direction.UP,
    Direction.DOWN: Direction.DOWN,
    Direction.DOWN_LEFT: Direction.DOWN,
    Direction.DOWN_RIGHT: Direction.DOWN,
    Direction.UP_LEFT: Direction.LEFT,
    Direction.UP_RIGHT: Direction.RIGHT,
}


def _adjust(direction: Direction) -> Direction:
    return _EIGHT_TO_FOUR[direction]
