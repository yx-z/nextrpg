from dataclasses import KW_ONLY, dataclass, field, replace
from enum import IntEnum
from functools import cached_property
from typing import Self, override

from frozendict import frozendict

from nextrpg.animation.cyclic_animation import CyclicAnimation
from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.config.character.rpg_maker_character_drawing_config import (
    RpgMakerCharacterDrawingConfig,
)
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.sprite_sheet import SpriteSheet, SpriteSheetSelection
from nextrpg.geometry.direction import Direction
from nextrpg.geometry.padding import Padding


class RpgMakerCharacterDrawingDefaultFrameType(IntEnum):
    _RIGHT_FOOT = 0
    _IDLE = 1
    _LEFT_FOOT = 2

    @classmethod
    def frame_indices(cls) -> tuple[int, ...]:
        return (
            RpgMakerCharacterDrawingDefaultFrameType._IDLE,
            RpgMakerCharacterDrawingDefaultFrameType._RIGHT_FOOT,
            RpgMakerCharacterDrawingDefaultFrameType._IDLE,
            RpgMakerCharacterDrawingDefaultFrameType._LEFT_FOOT,
        )


class RpgMakerCharacterDrawingXpFrameType(IntEnum):
    _IDLE = 0
    _RIGHT_FOOT = 1
    _IDLE_AGAIN = 2
    _LEFT_FOOT = 3

    @classmethod
    def frame_indices(cls) -> tuple[int, ...]:
        return tuple(cls)


type RpgMakerCharacterDrawingFrameType = type[
    RpgMakerCharacterDrawingDefaultFrameType
    | RpgMakerCharacterDrawingXpFrameType
]


@dataclass(frozen=True, kw_only=True)
class RpgMakerSpriteSheet(SpriteSheet):
    num_columns: int = 4
    num_rows: int = 2
    trim: Padding = Padding()
    style: RpgMakerCharacterDrawingFrameType = (
        RpgMakerCharacterDrawingDefaultFrameType
    )


@dataclass_with_default(kw_only=True, frozen=True)
class RpgMakerCharacterDrawing(CharacterDrawing):
    sprite_sheet: RpgMakerSpriteSheet
    direction: Direction = Direction.DOWN
    selection: SpriteSheetSelection | None = None
    animate_on_idle: bool = False
    config: RpgMakerCharacterDrawingConfig = field(
        default_factory=lambda: config().character.rpg_maker_character_drawing
    )
    _: KW_ONLY = private_init_below()
    _animations: frozendict[Direction, CyclicAnimation] = default(
        lambda self: self._init_animation
    )

    @override
    @cached_property
    def drawing(self) -> Drawing | DrawingGroup:
        adjusted_direction = _adjust(self.direction)
        return self._animations[adjusted_direction].drawing

    @override
    def turn(self, direction: Direction) -> Self:
        animation = {
            d: frames if d == _adjust(direction) else frames.reset
            for d, frames in self._animations.items()
        }
        return replace(self, direction=direction, _animations=animation)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        animation = {
            direction: self._tick_animation(time_delta, direction)
            for direction, frames in self._animations.items()
        }
        return replace(self, _animations=animation)

    @override
    def tick_idle(self, time_delta: Millisecond) -> Self:
        if self.animate_on_idle:
            return self.tick(time_delta)
        animation = {d: frames.reset for d, frames in self._animations.items()}
        return replace(self, _animations=animation)

    def _tick_animation(
        self, time_delta: Millisecond, adjusted_direction: Direction
    ) -> CyclicAnimation:
        animation = self._animations[adjusted_direction]
        if adjusted_direction == _adjust(self.direction):
            return animation.tick(time_delta)
        return animation

    def _load_row(self, drawing: Drawing, row: int) -> CyclicAnimation:
        frames = tuple(
            d.trim(self.sprite_sheet.trim)
            for d in self._crop_at_row(drawing, row)
        )
        ordered_frames = tuple(
            frames[i] for i in self.sprite_sheet.style.frame_indices()
        )
        return CyclicAnimation(
            frames=ordered_frames,
            duration_per_frame=self.config.duration_per_frame,
        )

    def _crop_at_row(self, drawing: Drawing, row: int) -> tuple[Drawing, ...]:
        num_frames = len(self.sprite_sheet.style)
        width = drawing.width / num_frames
        height = drawing.height / len(_DIR_TO_ROW)
        size = width * height
        height_shift = row * height
        return tuple(
            drawing.crop(
                ((width * i) * height_shift)
                .coordinate.as_top_left_of(size)
                .rectangle_area_on_screen
            )
            for i in range(num_frames)
        )

    @property
    def _init_animation(self) -> frozendict[Direction, CyclicAnimation]:
        if self.selection:
            drawing = self.sprite_sheet.select(self.selection)
        else:
            drawing = self.sprite_sheet.drawing
        res = {
            direction: self._load_row(drawing, row)
            for direction, row in _DIR_TO_ROW.items()
        }
        return frozendict(res)


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
