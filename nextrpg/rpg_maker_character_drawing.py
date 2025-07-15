"""
RPG Maker character drawing implementation for NextRPG.

This module provides functionality for rendering RPG Maker-style character
sprites with support for different sprite sheet formats and animation patterns.
It includes support for both RPG Maker VX/VX Ace/MV/MZ and XP sprite sheet
formats, with automatic frame extraction and animation handling.

The module supports various RPG Maker sprite sheet layouts, character
selection from multi-character sheets, frame trimming, and both idle
and movement animations. It's designed to be compatible with existing
RPG Maker resources while providing modern animation capabilities.

Note that `nextrpg` is only compatible with the RPG Maker character
sprite sheet to be able to re-use existing resources. However, using
RPG Maker's Runtime Time Package (RTP) in non-RPG Maker framework
violates the license of RPG Maker, even if you own a copy of RPG Maker.

Key Features:
    - RPG Maker VX/VX Ace/MV/MZ sprite sheet support
    - RPG Maker XP sprite sheet support
    - Multi-character sprite sheet selection
    - Frame trimming and cropping
    - Idle and movement animations
    - Configurable animation timing
    - Direction-based frame selection

Example:
    ```python
    from nextrpg.rpg_maker_character_drawing import (
        RpgMakerCharacterDrawing, SpriteSheet, SpriteSheetSelection
    )
    from nextrpg.draw_on_screen import Drawing

    # Create a sprite sheet configuration
    sprite_sheet = SpriteSheet(
        drawing=Drawing.load("characters.png"),
        style=DefaultFrameType
    )

    # Create character drawing
    character = RpgMakerCharacterDrawing(
        sprite_sheet=sprite_sheet,
        sprite_sheet_selection=SpriteSheetSelection(row=0, column=0),
        animate_on_idle=True
    )
    ```
"""

from dataclasses import dataclass, field, replace
from enum import IntEnum
from typing import Self, override

from nextrpg.character_drawing import CharacterDrawing
from nextrpg.coordinate import Coordinate
from nextrpg.core import Direction, Millisecond, Pixel
from nextrpg.draw_on_screen import Size
from nextrpg.draw_on_screen import Drawing
from nextrpg.frames import CyclicFrames
from nextrpg.global_config import config
from nextrpg.model import dataclass_with_instance_init, export, instance_init


@export
class DefaultFrameType(IntEnum):
    """
    RPG Maker VX/VX Ace/MV/MZ sprite sheet format (4 direction x 3 frames).

    This enum defines the frame indices for the standard RPG Maker
    sprite sheet format used in VX, VX Ace, MV, and MZ. Each
    direction has 3 frames: idle, right foot, and left foot.

    The frame sequence for walking animation is:
    idle -> right foot -> idle -> left foot -> idle

    Example:
        ```python
        from nextrpg.rpg_maker_character_drawing import DefaultFrameType

        # Use default RPG Maker format
        sprite_sheet = SpriteSheet(
            drawing=character_sprite,
            style=DefaultFrameType
        )
        ```
    """

    _RIGHT_FOOT = 0
    _IDLE = 1
    _LEFT_FOOT = 2

    @classmethod
    def _frame_indices(cls) -> tuple[int, ...]:
        """
        Get the frame indices for the walking animation sequence.

        Returns:
            `tuple[int, ...]`: Frame indices in animation order.
        """
        return (
            DefaultFrameType._IDLE,
            DefaultFrameType._RIGHT_FOOT,
            DefaultFrameType._IDLE,
            DefaultFrameType._LEFT_FOOT,
        )


@export
class XpFrameType(IntEnum):
    """
    RPG Maker XP sprite sheet format (4 direction x 4 frames).

    This enum defines the frame indices for the RPG Maker XP
    sprite sheet format. Each direction has 4 frames with a
    different animation sequence than the standard format.

    The frame sequence for walking animation is:
    idle -> right foot -> idle again -> left foot

    Example:
        ```python
        from nextrpg.rpg_maker_character_drawing import XpFrameType

        # Use RPG Maker XP format
        sprite_sheet = SpriteSheet(
            drawing=character_sprite,
            style=XpFrameType
        )
        ```
    """

    _IDLE = 0
    _RIGHT_FOOT = 1
    _IDLE_AGAIN = 2
    _LEFT_FOOT = 3

    @classmethod
    def _frame_indices(cls) -> tuple[int, ...]:
        """
        Get the frame indices for the walking animation sequence.

        Returns:
            `tuple[int, ...]`: Frame indices in animation order.
        """
        return tuple(cls)


type FrameType = type[DefaultFrameType | XpFrameType]
"""
Choose between DefaultFrameType and XpFrameType.

This type alias allows selecting between the two RPG Maker
sprite sheet formats when creating character drawings.
"""


@export
@dataclass(frozen=True)
class SpriteSheetSelection:
    """
    Zero-indexed row/column for selecting a portion of a sprite sheet.

    This class defines the position and boundaries for extracting a
    specific character sprite sheet from a larger sprite sheet containing
    multiple characters. It supports both single-character and
    multi-character sprite sheets.

    Arguments:
        `row`: Row index of the character in the sprite sheet.

        `column`: Column index of the character in the sprite sheet.

        `max_rows`: Total number of rows in the sprite sheet.
            Defaults to two rows.

        `max_columns`: Total number of columns in the sprite sheet.
            Defaults to four columns.

    Example:
        ```python
        from nextrpg.rpg_maker_character_drawing import SpriteSheetSelection

        # Select first character (top-left)
        selection = SpriteSheetSelection(row=0, column=0)

        # Select second character in first row
        selection = SpriteSheetSelection(row=0, column=1)

        # Custom sprite sheet layout
        selection = SpriteSheetSelection(
            row=1, column=2,
            max_rows=3, max_columns=4
        )
        ```
    """

    row: int
    column: int
    max_rows: int = 2
    max_columns: int = 4


@export
@dataclass(frozen=True)
class Trim:
    """
    Trim settings for cropping individual character frames.

    This class defines the trimming parameters for removing
    unwanted pixels from character frames. Useful for removing
    transparent borders or adjusting character positioning.

    Arguments:
        `top`: Number of pixels to trim from the top.

        `left`: Number of pixels to trim from the left.

        `bottom`: Number of pixels to trim from the bottom.

        `right`: Number of pixels to trim from the right.

    Example:
        ```python
        from nextrpg.rpg_maker_character_drawing import Trim

        # Remove 2 pixels from all sides
        trim = Trim(top=2, left=2, bottom=2, right=2)

        # Only trim from bottom
        trim = Trim(bottom=4)
        ```
    """

    top: Pixel = 0
    left: Pixel = 0
    bottom: Pixel = 0
    right: Pixel = 0


@export
@dataclass(frozen=True)
class SpriteSheet:
    """
    Container for sprite sheet configuration.

    This class holds all necessary information to process and render
    character sprites from a sprite sheet image. It includes the
    drawing, trimming settings, and frame type specification.

    Arguments:
        `drawing`: The sprite sheet image to process.

        `trim`: Trimming settings for individual frames.
            Defaults to no trimming.

        `style`: The sprite sheet format style to use.
            Defaults to DefaultFrameType.

    Example:
        ```python
        from nextrpg.rpg_maker_character_drawing import SpriteSheet
        from nextrpg.draw_on_screen import Drawing

        # Create sprite sheet configuration
        sprite_sheet = SpriteSheet(
            drawing=Drawing.load("characters.png"),
            trim=Trim(bottom=2),
            style=DefaultFrameType
        )
        ```
    """

    drawing: Drawing
    trim: Trim = Trim()
    style: FrameType = DefaultFrameType


def _init_frames(
    self: RpgMakerCharacterDrawing,
) -> dict[Direction, CyclicFrames]:
    """
    Initialize animation frames for all directions.

    Creates CyclicFrames for each direction by extracting
    the appropriate row from the sprite sheet and processing
    the frames according to the selected format.

    Arguments:
        `self`: The RpgMakerCharacterDrawing instance.

    Returns:
        `dict[Direction, CyclicFrames]`: Animation frames for each direction.

    Example:
        ```python
        frames = _init_frames(character_drawing)
        ```
    """
    drawing = (
        self._crop_by_selection(self.sprite_sheet_selection)
        if self.sprite_sheet_selection
        else self.sprite_sheet.drawing
    )
    return {
        direction: self._load_frames_row(drawing, row)
        for direction, row in _DIR_TO_ROW.items()
    }


@export
@dataclass_with_instance_init
class RpgMakerCharacterDrawing(CharacterDrawing):
    """
    RPG Maker style character drawing with animation support.

    This class provides RPG Maker-compatible character rendering
    with support for different sprite sheet formats, multi-character
    selection, and both idle and movement animations.

    The character supports eight directions of movement, configurable
    animation timing, and optional idle animations. It automatically
    handles frame extraction and animation sequencing based on the
    selected sprite sheet format.

    Arguments:
        `sprite_sheet`: Configuration for the character's sprite sheet.

        `sprite_sheet_selection`: Selection for multi-character sheets.
            If None, uses the entire sprite sheet.

        `animate_on_idle`: Whether to animate the character when not moving.
            Defaults to False.

        `duration_per_frame`: Duration for each animation frame in milliseconds.
            If not specified, uses the default from configuration.

        `_frames`: Internal animation frames for each direction.
            Initialized automatically from the sprite sheet.

    Example:
        ```python
        from nextrpg.rpg_maker_character_drawing import RpgMakerCharacterDrawing

        # Create a character with idle animation
        character = RpgMakerCharacterDrawing(
            sprite_sheet=sprite_sheet,
            animate_on_idle=True,
            duration_per_frame=200
        )

        # Update character animation
        character = character.tick_move(time_delta)
        ```
    """

    sprite_sheet: SpriteSheet
    sprite_sheet_selection: SpriteSheetSelection | None = None
    animate_on_idle: bool = False
    duration_per_frame: Millisecond = field(
        default_factory=lambda: config().rpg_maker_character.duration_per_frame
    )
    _frames: dict[Direction, CyclicFrames] = instance_init(_init_frames)

    @property
    def drawing(self) -> Drawing:
        """
        Get the current frame drawing for the character.

        Returns the current animation frame for the character's
        current direction.

        Returns:
            `Drawing`: The current character frame.

        Example:
            ```python
            current_frame = character.drawing
            ```
        """
        return self._frames[_adjust(self.direction)].current_frame

    @override
    def turn(self, direction: Direction) -> Self:
        """
        Turn the character to face a new direction.

        Updates the character's direction and resets animation
        frames for all directions except the new direction.

        Arguments:
            `direction`: The new direction to face.

        Returns:
            `RpgMakerCharacterDrawing`: The updated character state.

        Example:
            ```python
            # Turn character to face up
            character = character.turn(Direction.UP)
            ```
        """
        return replace(
            self,
            direction=direction,
            _frames={
                d: frames if d == _adjust(direction) else frames.reset
                for d, frames in self._frames.items()
            },
        )

    @override
    def tick_move(self, time_delta: Millisecond) -> Self:
        """
        Update the character's movement animation.

        Advances the animation frames for all directions based
        on the elapsed time, with the current direction being
        the only one that actually animates.

        Arguments:
            `time_delta`: The time elapsed since the last update
                in milliseconds.

        Returns:
            `RpgMakerCharacterDrawing`: The updated character state.

        Example:
            ```python
            # Update movement animation
            character = character.tick_move(time_delta)
            ```
        """
        return replace(
            self,
            _frames={
                direction: self._tick_frames(time_delta, direction)
                for direction, frames in self._frames.items()
            },
        )

    def _tick_frames(
        self, time_delta: Millisecond, adjusted_direction: Direction
    ) -> CyclicFrames:
        """
        Update animation frames for a specific direction.

        Arguments:
            `time_delta`: The time elapsed since the last update.

            `adjusted_direction`: The direction to update frames for.

        Returns:
            `CyclicFrames`: The updated animation frames.

        Example:
            ```python
            frames = character._tick_frames(time_delta, Direction.UP)
            ```
        """
        frames = self._frames[adjusted_direction]
        if adjusted_direction == _adjust(self.direction):
            return frames.tick(time_delta)
        return frames

    @override
    def tick_idle(self, time_delta: Millisecond) -> Self:
        """
        Update the character's idle animation.

        If idle animation is enabled, advances the movement
        animation. Otherwise, resets all animation frames
        to their initial state.

        Arguments:
            `time_delta`: The time elapsed since the last update
                in milliseconds.

        Returns:
            `RpgMakerCharacterDrawing`: The updated character state.

        Example:
            ```python
            # Update idle animation
            character = character.tick_idle(time_delta)
            ```
        """
        if self.animate_on_idle:
            return self.tick_move(time_delta)
        return replace(
            self,
            _frames={d: frames.reset for d, frames in self._frames.items()},
        )

    def _crop_by_selection(self, selection: SpriteSheetSelection) -> Drawing:
        """
        Crop the sprite sheet to select a specific character.

        Arguments:
            `selection`: The character selection parameters.

        Returns:
            `Drawing`: The cropped sprite sheet for the selected character.

        Example:
            ```python
            cropped = character._crop_by_selection(selection)
            ```
        """
        drawing = self.sprite_sheet.drawing
        width = drawing.width / selection.max_columns
        height = drawing.height / selection.max_rows
        return drawing.crop(
            Coordinate(width * selection.column, height * selection.row),
            Size(width, height),
        )

    def _load_frames_row(self, drawing: Drawing, row: int) -> CyclicFrames:
        """
        Load animation frames from a specific row of the sprite sheet.

        Arguments:
            `drawing`: The sprite sheet drawing to process.

            `row`: The row index to extract frames from.

        Returns:
            `CyclicFrames`: The animation frames for the row.

        Example:
            ```python
            frames = character._load_frames_row(sprite_sheet, 0)
            ```
        """
        frames = [
            self._trim(d) for d in self._crop_into_frames_at_row(drawing, row)
        ]
        return CyclicFrames(
            frames=tuple(
                frames[i] for i in self.sprite_sheet.style._frame_indices()
            ),
            duration_per_frame=self.duration_per_frame,
        )

    def _crop_into_frames_at_row(
        self, drawing: Drawing, row: int
    ) -> tuple[Drawing, ...]:
        """
        Crop the sprite sheet into individual frames for a row.

        Arguments:
            `drawing`: The sprite sheet drawing to process.

            `row`: The row index to extract frames from.

        Returns:
            `tuple[Drawing, ...]`: Individual frame drawings.

        Example:
            ```python
            frames = character._crop_into_frames_at_row(sprite_sheet, 0)
            ```
        """
        num_frames = len(self.sprite_sheet.style)
        width = drawing.width / num_frames
        height = drawing.height / 4
        return tuple(
            drawing.crop(
                Coordinate(width * i, height * row), Size(width, height)
            )
            for i in range(num_frames)
        )

    def _trim(self, drawing: Drawing) -> Drawing:
        """
        Apply trimming to a character frame.

        Arguments:
            `drawing`: The frame drawing to trim.

        Returns:
            `Drawing`: The trimmed frame drawing.

        Example:
            ```python
            trimmed = character._trim(frame_drawing)
            ```
        """
        trim = self.sprite_sheet.trim
        return drawing.crop(
            Coordinate(trim.left, trim.top),
            Size(
                drawing.width - trim.left - trim.right,
                drawing.height - trim.top - trim.bottom,
            ),
        )


# Direction to row mapping for RPG Maker sprite sheets
_DIR_TO_ROW = {
    Direction.DOWN: 0,
    Direction.LEFT: 1,
    Direction.RIGHT: 2,
    Direction.UP: 3,
}


def _adjust(direction: Direction) -> Direction:
    """
    Adjust direction to RPG Maker sprite sheet format.

    RPG Maker sprite sheets only support four directions
    (up, down, left, right), so diagonal directions are
    mapped to the nearest cardinal direction.

    Arguments:
        `direction`: The direction to adjust.

    Returns:
        `Direction`: The adjusted direction for sprite sheet lookup.

    Example:
        ```python
        adjusted = _adjust(Direction.UP_LEFT)  # Returns Direction.UP
        ```
    """
    if direction in (Direction.UP_LEFT, Direction.UP_RIGHT):
        return Direction.UP
    if direction in (Direction.DOWN_LEFT, Direction.DOWN_RIGHT):
        return Direction.DOWN
    return direction
