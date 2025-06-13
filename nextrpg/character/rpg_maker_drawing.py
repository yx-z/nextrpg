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
from enum import Enum, IntEnum, auto
from typing import Final, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.common_types import Direction, Millisecond, Pixel
from nextrpg.config import config
from nextrpg.draw_on_screen import Coordinate, Drawing, Size
from nextrpg.frames import FrameExhaustedOption, FrameIndex, Frames
from nextrpg.util import assert_not_none


class Style(Enum):
    """
    Sprite sheet style enumeration.

    Defines different RPG Maker sprite sheet formats that can be used
    for character animation.

    Arguments:
        `DEFAULT`: RPG Maker VX/VX Ace/MV/MZ sprite sheet format.

        `XP`: RPG Maker XP style sprite sheet format.
    """

    DEFAULT = auto()
    XP = auto()


@dataclass(frozen=True)
class SpriteSheetSelection:
    """
    Configuration for selecting a portion of a sprite sheet.

    Defines the position and boundaries for extracting a specific character sprite
    from a larger sprite sheet containing multiple characters.

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
class Margin:
    """
    Margin settings for sprite sheet frames.

    Defines the padding around individual sprite frames that should be trimmed
    during rendering.

    Arguments:
        `top`: Number of pixels to trim from the top.

        `bottom`: Number of pixels to trim from the bottom.

        `left`: Number of pixels to trim from the left.

        `right`: Number of pixels to trim from the right.
    """

    top: Pixel = 0
    bottom: Pixel = 0
    left: Pixel = 0
    right: Pixel = 0


@dataclass(frozen=True)
class SpriteSheet:
    """
    Container for sprite sheet configuration.

    Holds all necessary information to process and render character sprites
    from a sprite sheet image.

    Arguments:
        `drawing`: The sprite sheet image to process.

        `selection`: Optional for selecting a portion of the sprite sheet.

        `margin`: Margin settings for trimming individual frames.

        `style`: The sprite sheet format style to use.
    """

    drawing: Drawing
    selection: SpriteSheetSelection | None = None
    margin: Margin = Margin()
    style: Style = Style.DEFAULT


class RpgMakerCharacterDrawing(CharacterDrawing):
    """
    RPG Maker style character drawing implementation.

    Handles character animation using RPG Maker style sprite sheets with support
    for different directions and movement states.

    Arguments:
        `sprite_sheet`: Configuration for the character's sprite sheet.

        `animate_on_idle`: Whether to animate the character when not moving.

        `frame_duration`: Duration for each animation frame in milliseconds.
            If not specified, the default duration from `Config` is used.
    """

    def __init__(
        self,
        sprite_sheet: SpriteSheet,
        animate_on_idle: bool = False,
        frame_duration: Millisecond | None = None,
    ) -> None:
        self._frames: Final[dict[Direction, Frames]] = _load_sprite_frames(
            sprite_sheet
        )
        self._animate_on_idle: Final[bool] = animate_on_idle
        self._frame_duration: Final[Millisecond] = (
            frame_duration
            or config().rpg_maker_character_sprite.default_frame_duration
        )
        self._frame_elapsed = 0

    @override
    def draw(
        self, time_delta: Millisecond, direction: Direction, is_moving: bool
    ) -> Drawing:
        """
        The `draw` method determines the appropriate sprite frame to display
        based on the direction, movement state, and elapsed time.
        It adjusts the direction of the sprite,
        calculates frame timing for animations, and handles transitioning to
        the next or current frame of the sprite animation.

        Arguments:
            `time_delta`:
                The time in milliseconds that has passed since the last frame.
                This is used to calculate the frame timing for animations.

            `direction`:
                The direction in which the object is currently facing or moving.
                This affects the selection of the sprite frame.

            `is_moving`: Indicates if the object is in motion.
                This affects whether animations for the sprite
                are played or reset.

        Returns:
            `Drawing`:
                An object that represents the current frame or sprite based on
                the direction and movement state of the object.
        """
        adjusted_direction = _EIGHT_TO_FOUR[direction]
        for other_direction in filter(
            lambda d: d != adjusted_direction, self._frames
        ):
            self._frames[other_direction].reset()

        if is_moving or self._animate_on_idle:
            self._frame_elapsed += time_delta
            if self._frame_elapsed > self._frame_duration:
                self._frame_elapsed = 0
                return assert_not_none(
                    self._frames[adjusted_direction].next_frame()
                )
        else:
            self._frames[adjusted_direction].reset()
        return assert_not_none(self._frames[adjusted_direction].current_frame())


class _DefaultFrameType(IntEnum):
    RIGHT = 0
    IDLE = 1
    LEFT = 2

    @classmethod
    def frame_indices(cls) -> list[FrameIndex]:
        return [
            _DefaultFrameType.IDLE,
            _DefaultFrameType.RIGHT,
            _DefaultFrameType.IDLE,
            _DefaultFrameType.LEFT,
        ]


class _XpFrameType(IntEnum):
    IDLE = 0
    RIGHT = 1
    IDLE_AGAIN = 2
    LEFT = 3

    @classmethod
    def frame_indices(cls) -> list[FrameIndex]:
        return list(cls)


def _crop_margin(drawing: Drawing, margin: Margin) -> Drawing:
    return drawing.crop(
        Coordinate(margin.left, margin.top),
        Size(
            drawing.width - margin.left - margin.right,
            drawing.height - margin.top - margin.bottom,
        ),
    )


def _crop_into_frames_at_row(
    drawing: Drawing, row: int, num_frames: int, margin: Margin
) -> list[Drawing]:
    width = drawing.width / num_frames
    height = drawing.height / 4
    return [
        _crop_margin(
            drawing.crop(
                Coordinate(width * i, height * row), Size(width, height)
            ),
            margin,
        )
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


def _load_sprite_frames(sprite_sheet: SpriteSheet) -> dict[Direction, Frames]:
    drawing = (
        _crop_by_selection(sprite_sheet.drawing, sprite_sheet.selection)
        if sprite_sheet.selection
        else sprite_sheet.drawing
    )
    return {
        direction: Frames(
            _crop_into_frames_at_row(
                drawing,
                row,
                len(frame_type := _FRAME_TYPES[sprite_sheet.style]),
                sprite_sheet.margin,
            ),
            FrameExhaustedOption.CYCLE,
            frame_type.frame_indices(),
        )
        for direction, row in _DIRECTION_TO_ROW.items()
    }


_FRAME_TYPES: dict[Style, type[_DefaultFrameType | _XpFrameType]] = {
    Style.DEFAULT: _DefaultFrameType,
    Style.XP: _XpFrameType,
}

_DIRECTION_TO_ROW = {
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
    Direction.UP_LEFT: Direction.UP,
    Direction.UP_RIGHT: Direction.UP,
}
