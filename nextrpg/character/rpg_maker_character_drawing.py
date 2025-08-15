from dataclasses import KW_ONLY, dataclass, field, replace
from enum import IntEnum
from typing import Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.dimension import Size
from nextrpg.core.direction import Direction
from nextrpg.core.time import Millisecond
from nextrpg.draw.cyclic_frames import CyclicFrames
from nextrpg.draw.drawing import Drawing, Trim
from nextrpg.draw.sprite_sheet import SpriteSheet, SpriteSheetSelection
from nextrpg.global_config.global_config import config


class DefaultFrameType(IntEnum):
    _RIGHT_FOOT = 0
    _IDLE = 1
    _LEFT_FOOT = 2

    @classmethod
    def _frame_indices(cls) -> tuple[int, ...]:
        return (
            DefaultFrameType._IDLE,
            DefaultFrameType._RIGHT_FOOT,
            DefaultFrameType._IDLE,
            DefaultFrameType._LEFT_FOOT,
        )


class XpFrameType(IntEnum):
    _IDLE = 0
    _RIGHT_FOOT = 1
    _IDLE_AGAIN = 2
    _LEFT_FOOT = 3

    @classmethod
    def _frame_indices(cls) -> tuple[int, ...]:
        return tuple(cls)


type FrameType = type[DefaultFrameType | XpFrameType]


@dataclass(frozen=True, kw_only=True)
class RpgMakerSpriteSheet(SpriteSheet):
    trim: Trim | None = None
    num_column: int = 4
    num_row: int = 2
    style: FrameType = DefaultFrameType


@dataclass_with_init(frozen=True)
class RpgMakerCharacterDrawing(CharacterDrawing):
    sprite_sheet: RpgMakerSpriteSheet
    selection: SpriteSheetSelection | None = None
    animate_on_idle: bool = False
    duration_per_frame: Millisecond = field(
        default_factory=lambda: config().rpg_maker_character.duration_per_frame
    )
    _: KW_ONLY = not_constructor_below()
    _frames: dict[Direction, CyclicFrames] = default(
        lambda self: self._init_frames
    )

    @property
    def drawing(self) -> Drawing:
        return self._frames[_adjust(self.direction)].drawing

    @override
    def turn(self, direction: Direction) -> Self:
        frames = {
            d: frames if d == _adjust(direction) else frames.reset
            for d, frames in self._frames.items()
        }
        return replace(self, direction=direction, _frames=frames)

    @override
    def tick_move(self, time_delta: Millisecond) -> Self:
        frames = {
            direction: self._tick_frames(time_delta, direction)
            for direction, frames in self._frames.items()
        }
        return replace(self, _frames=frames)

    @override
    def tick_idle(self, time_delta: Millisecond) -> Self:
        if self.animate_on_idle:
            return self.tick_move(time_delta)
        frames = {d: frames.reset for d, frames in self._frames.items()}
        return replace(self, _frames=frames)

    def _tick_frames(
        self, time_delta: Millisecond, adjusted_direction: Direction
    ) -> CyclicFrames:
        frames = self._frames[adjusted_direction]
        if adjusted_direction == _adjust(self.direction):
            return frames.tick(time_delta)
        return frames

    def _trim(self, draw: Drawing) -> Drawing:
        if self.sprite_sheet.trim:
            return draw.trim(self.sprite_sheet.trim)
        return draw

    def _load_frames_row(self, draw: Drawing, row: int) -> CyclicFrames:
        frames = tuple(
            self._trim(d) for d in self._crop_into_frames_at_row(draw, row)
        )
        ordered_frames = tuple(
            frames[i] for i in self.sprite_sheet.style._frame_indices()
        )
        return CyclicFrames(
            frames=ordered_frames, duration_per_frame=self.duration_per_frame
        )

    def _crop_into_frames_at_row(
        self, draw: Drawing, row: int
    ) -> tuple[Drawing, ...]:
        num_frames = len(self.sprite_sheet.style)
        width = draw.width / num_frames
        height = draw.height / len(_DIR_TO_ROW)
        size = Size(width, height)
        return tuple(
            draw.crop(Coordinate(width * i, height * row), size)
            for i in range(num_frames)
        )

    @property
    def _init_frames(self) -> dict[Direction, CyclicFrames]:
        if self.selection:
            draw = self.sprite_sheet.select(self.selection)
        else:
            draw = self.sprite_sheet.drawing
        return {
            direction: self._load_frames_row(draw, row)
            for direction, row in _DIR_TO_ROW.items()
        }


_DIR_TO_ROW = {
    Direction.DOWN: 0,
    Direction.LEFT: 1,
    Direction.RIGHT: 2,
    Direction.UP: 3,
}


def _adjust(direction: Direction) -> Direction:
    if direction in (Direction.UP_LEFT, Direction.UP_RIGHT):
        return Direction.UP
    if direction in (Direction.DOWN_LEFT, Direction.DOWN_RIGHT):
        return Direction.DOWN
    return direction
