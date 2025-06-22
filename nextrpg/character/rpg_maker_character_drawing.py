"""
RPG Maker character drawing implementation.

This module provides functionality for rendering RPG Maker-style character
drawing with support for different sprite sheet formats and animation patterns.

Note that `nextrpg` is only compatible with the
RPG Maker character sprite sheet, to be able to re-use existing resources.

However, using RPG Maker's
[Runtime Time Package (RTP)](https://www.rpgmakerweb.com/run-time-package)
in non-RPG Maker framework violates the license of RPG Maker,
even if you own a copy of RPG Maker.
"""

from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field, replace
from enum import IntEnum
from functools import cached_property
from typing import override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.config import config
from nextrpg.core import (
    Direction,
    Millisecond,
    Pixel,
)
from nextrpg.draw_on_screen import Coordinate, Drawing, Size
from nextrpg.frames import CyclicFrames
from nextrpg.model import initialize_internal_field, internal_field

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


@dataclass(frozen=True)
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
    animate_on_idle: bool = field(
        default_factory=lambda: config().rpg_maker_character.animate_on_idle
    )
    direction: Direction = field(
        default_factory=lambda: config().rpg_maker_character.direction
    )
    frame_duration: Millisecond = field(
        default_factory=lambda: config().rpg_maker_character.frame_duration
    )
    _: KW_ONLY = internal_field()
    _frames: dict[Direction, CyclicFrames] = internal_field()

    @cached_property
    @override
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

        Args:
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

        Args:
            `time_delta`: The amount of time that has
                passed since the last update.

        Returns:
            `CharacterDrawing`: The updated drawing with a new animation state
            for the current direction.
        """
        return replace(
            self,
            _frames={
                direction: (
                    frames.step(time_delta)
                    if direction == _adjust(self.direction)
                    else frames
                )
                for direction, frames in self._frames.items()
            },
        )

    @override
    def idle(self, time_delta: Millisecond) -> CharacterDrawing:
        """
        Update the character's idle animation state over the given time delta.

        If animate_on_idle is enabled, continues cycling through animation
        frames even when idle.
        Otherwise, resets all frames to their initial state.

        Args:
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

    def __post_init__(self) -> None:
        initialize_internal_field(
            self,
            "_frames",
            _load_frames,
            self.sprite_sheet,
            self.frame_duration,
        )


def _crop_margin(drawing: Drawing, margin: Margin) -> Drawing:
    return drawing.crop(
        Size(
            drawing.width - margin.left - margin.right,
            drawing.height - margin.top - margin.bottom,
        ),
        Coordinate(margin.left, margin.top),
    )


def _crop_into_frames_at_row(
    drawing: Drawing, sprite_sheet: SpriteSheet, row: int
) -> list[Drawing]:
    num_frames = len(sprite_sheet.style)
    width = drawing.width / num_frames
    height = drawing.height / 4
    return [
        drawing.crop(Size(width, height), Coordinate(width * i, height * row))
        for i in range(num_frames)
    ]


def _crop_by_selection(
    drawing: Drawing, selection: SpriteSheetSelection
) -> Drawing:
    width = drawing.width / selection.max_columns
    height = drawing.height / selection.max_rows
    return drawing.crop(
        Size(width, height),
        Coordinate(width * selection.column, height * selection.row),
    )


def _load_frames_row(
    drawing: Drawing,
    sprite_sheet: SpriteSheet,
    row: int,
    frame_duration: Millisecond,
) -> CyclicFrames:
    frames = [
        _crop_margin(d, sprite_sheet.margin)
        for d in _crop_into_frames_at_row(drawing, sprite_sheet, row)
    ]
    frame_indices = sprite_sheet.style._frame_indices()
    return CyclicFrames([frames[i] for i in frame_indices], frame_duration)


def _load_frames(
    sprite_sheet: SpriteSheet, frame_duration: Millisecond
) -> dict[Direction, CyclicFrames]:
    drawing = (
        _crop_by_selection(sprite_sheet.drawing, sprite_sheet.selection)
        if sprite_sheet.selection
        else sprite_sheet.drawing
    )
    return {
        d: _load_frames_row(drawing, sprite_sheet, row, frame_duration)
        for d, row in {
            Direction.DOWN: 0,
            Direction.LEFT: 1,
            Direction.RIGHT: 2,
            Direction.UP: 3,
        }.items()
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
