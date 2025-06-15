"""
RPG Maker character drawing implementation.

This module provides functionality for rendering RPG Maker-style character
sprites with support for different sprite sheet formats and animation patterns.

Note that `nextrpg` is only compatible with RPG Maker character sprite,
to be able to re-use existing resources.

However, using RPG Maker's
[Runtime Time Package (RTP)](https://www.rpgmakerweb.com/run-time-package)
in non-RPG Maker framework violates the license of RPG Maker,
even if you own a copy of RPG Maker.
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.common_types import Direction, Millisecond
from nextrpg.config import config
from nextrpg.draw_on_screen import Coordinate, Drawing, Size
from nextrpg.frames import CyclicFrames, FrameIndex


class DefaultFrameType(IntEnum):
    """
    RPG Maker VX/VX Ace/MV/MZ sprite sheet format (4 direction x 3 frames).
    """

    _RIGHT_FOOT = 0
    _IDLE = 1
    _LEFT_FOOT = 2

    @classmethod
    def frame_indices(cls) -> list[FrameIndex]:
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
    def frame_indices(cls) -> list[FrameIndex]:
        return list(cls)


type FrameType = type[DefaultFrameType | XpFrameType]


@dataclass(frozen=True)
class SpriteSheetSelection:
    """
    Configuration for selecting a portion of a sprite sheet.

    Defines the position and boundaries for extracting a specific character
    sprite from a larger sprite sheet containing multiple characters.

    Arguments:
        `row`: Row index of the character sprite in the sprite sheet.

        `column`: Column index of the character sprite in the sprite sheet.

        `max_rows`: Total number of rows in the sprite sheet.

        `max_columns`: Total number of columns in the sprite sheet.
    """

    row: int
    column: int
    max_rows: int = 2
    max_columns: int = 4


@dataclass(frozen=True)
class SpriteSheet:
    """
    Container for sprite sheet configuration.

    Holds all necessary information to process and render character sprites
    from a sprite sheet image.

    Arguments:
        `drawing`: The sprite sheet image to process.

        `selection`: Optional for selecting a portion of the sprite sheet.

        `style`: The sprite sheet format style to use.
    """

    drawing: Drawing
    selection: SpriteSheetSelection | None = None
    style: FrameType = DefaultFrameType


def load_sprite_sheet(
    sprite_sheet: SpriteSheet,
    animate_on_idle: bool = False,
    frame_duration: Millisecond | None = None,
) -> CharacterDrawing:
    """
    Load RPG Maker style character drawing.

    Arguments:
        `sprite_sheet`: Configuration for the character's sprite sheet.

        `animate_on_idle`: Whether to animate the character when not moving.

        `frame_duration`: Duration for each animation frame in milliseconds.
            If not specified, the default duration from `Config` is used.
    """
    return _RpgMakerCharacterDrawing(
        animate_on_idle,
        _load_sprite_frames(
            sprite_sheet,
            frame_duration
            or config().rpg_maker_character_sprite.default_frame_duration,
        ),
    )


@dataclass(frozen=True)
class _RpgMakerCharacterDrawing(CharacterDrawing):
    _animate_on_idle: bool
    _frames: dict[Direction, CyclicFrames]

    @override
    def draw_move(self, direction: Direction) -> Drawing:
        return self._current_frame(direction)

    @override
    def peek_move(
        self, time_delta: Millisecond, direction: Direction
    ) -> Drawing:
        return self._frames[_adjust(direction)].peek(time_delta)

    @override
    def move(
        self, time_delta: Millisecond, direction: Direction
    ) -> CharacterDrawing:
        return _RpgMakerCharacterDrawing(
            self._animate_on_idle,
            {
                d: (
                    frames.step(time_delta)
                    if d == _adjust(direction)
                    else frames.reset()
                )
                for d, frames in self._frames.items()
            },
        )

    @override
    def draw_idle(self, direction: Direction) -> Drawing:
        return self._current_frame(direction)

    @override
    def idle(self, time_delta: Millisecond, direction) -> "CharacterDrawing":
        return (
            self.move(time_delta, direction)
            if self._animate_on_idle
            else self.stop()
        )

    @override
    def stop(self) -> CharacterDrawing:
        return _RpgMakerCharacterDrawing(
            self._animate_on_idle,
            {d: frames.reset() for d, frames in self._frames.items()},
        )

    def _current_frame(self, direction: Direction) -> Drawing:
        return self._frames[_adjust(direction)].current_frame


def _crop_into_frames_at_row(
    drawing: Drawing, frame_type: FrameType, row: int
) -> list[Drawing]:
    num_frames = len(frame_type)
    width = drawing.width / num_frames
    height = drawing.height / 4
    return [
        drawing.crop(Coordinate(width * i, height * row), Size(width, height))
        for i in range(num_frames)
    ]


def _crop_by_selection(
    drawing: Drawing, selection: SpriteSheetSelection
) -> Drawing:
    return drawing.crop(
        Coordinate(
            (width := drawing.width / selection.max_columns) * selection.column,
            (height := drawing.height / selection.max_rows) * selection.row,
        ),
        Size(width, height),
    )


def _load_frames_row(
    drawing: Drawing,
    frame_type: FrameType,
    row: int,
    frame_duration: Millisecond,
) -> CyclicFrames:
    frames = _crop_into_frames_at_row(drawing, frame_type, row)
    return CyclicFrames(
        [frames[i] for i in frame_type.frame_indices()], frame_duration
    )


def _load_sprite_frames(
    sprite_sheet: SpriteSheet, frame_duration: Millisecond
) -> dict[Direction, CyclicFrames]:
    drawing = (
        _crop_by_selection(sprite_sheet.drawing, sprite_sheet.selection)
        if sprite_sheet.selection
        else sprite_sheet.drawing
    )
    return {
        d: _load_frames_row(drawing, sprite_sheet.style, row, frame_duration)
        for d, row in {
            Direction.DOWN: 0,
            Direction.LEFT: 1,
            Direction.RIGHT: 2,
            Direction.UP: 3,
        }.items()
    }


def _adjust(direction: Direction) -> Direction:
    return {
        Direction.RIGHT: Direction.RIGHT,
        Direction.LEFT: Direction.LEFT,
        Direction.UP: Direction.UP,
        Direction.DOWN: Direction.DOWN,
        Direction.DOWN_LEFT: Direction.DOWN,
        Direction.DOWN_RIGHT: Direction.DOWN,
        Direction.UP_LEFT: Direction.LEFT,
        Direction.UP_RIGHT: Direction.RIGHT,
    }[direction]
