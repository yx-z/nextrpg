from dataclasses import KW_ONLY, dataclass, field, replace
from enum import IntEnum
from typing import Self, override

from nextrpg.animation.cyclic_animation import CyclicAnimation
from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default_init import (
    dataclass_with_default_init,
    default_init,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_trim import DrawingTrim
from nextrpg.draw.sprite_sheet import SpriteSheet, SpriteSheetSelection
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.direction import Direction
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen


class DefaultCharacterDrawingType(IntEnum):
    _RIGHT_FOOT = 0
    _IDLE = 1
    _LEFT_FOOT = 2

    @classmethod
    def _frame_indices(cls) -> tuple[int, ...]:
        return (
            DefaultCharacterDrawingType._IDLE,
            DefaultCharacterDrawingType._RIGHT_FOOT,
            DefaultCharacterDrawingType._IDLE,
            DefaultCharacterDrawingType._LEFT_FOOT,
        )


class RpgMakerXpCharacterDrawingType(IntEnum):
    _IDLE = 0
    _RIGHT_FOOT = 1
    _IDLE_AGAIN = 2
    _LEFT_FOOT = 3

    @classmethod
    def _frame_indices(cls) -> tuple[int, ...]:
        return tuple(cls)


type FrameType = type[
    DefaultCharacterDrawingType | RpgMakerXpCharacterDrawingType
]


@dataclass(frozen=True, kw_only=True)
class RpgMakerSpriteSheet(SpriteSheet):
    num_column: int = 4
    num_row: int = 2
    trim: DrawingTrim | None = None
    style: FrameType = DefaultCharacterDrawingType


@dataclass_with_default_init(frozen=True)
class RpgMakerCharacterDrawing(CharacterDrawing):
    sprite_sheet: RpgMakerSpriteSheet
    selection: SpriteSheetSelection | None = None
    animate_on_idle: bool = False
    duration_per_frame: Millisecond = field(
        default_factory=lambda: config().rpg_maker_character.duration_per_frame
    )
    _: KW_ONLY = not_constructor_below()
    _animations: dict[Direction, CyclicAnimation] = default_init(
        lambda self: self._init_animation
    )

    @property
    def drawing(self) -> Drawing:
        return self._animations[_adjust(self.direction)].drawing

    @override
    def turn(self, direction: Direction) -> Self:
        animation = {
            d: frames if d == _adjust(direction) else frames.reset
            for d, frames in self._animations.items()
        }
        return replace(self, direction=direction, _animations=animation)

    @override
    def tick_move(self, time_delta: Millisecond) -> Self:
        animation = {
            direction: self._tick_animation(time_delta, direction)
            for direction, frames in self._animations.items()
        }
        return replace(self, _animations=animation)

    @override
    def tick_idle(self, time_delta: Millisecond) -> Self:
        if self.animate_on_idle:
            return self.tick_move(time_delta)
        animation = {d: frames.reset for d, frames in self._animations.items()}
        return replace(self, _animations=animation)

    def _tick_animation(
        self, time_delta: Millisecond, adjusted_direction: Direction
    ) -> CyclicAnimation:
        animation = self._animations[adjusted_direction]
        if adjusted_direction == _adjust(self.direction):
            return animation.tick(time_delta)
        return animation

    def _trim(self, drawing: Drawing) -> Drawing:
        if self.sprite_sheet.trim:
            return drawing.trim(self.sprite_sheet.trim)
        return drawing

    def _load_row(self, drawing: Drawing, row: int) -> CyclicAnimation:
        frames = tuple(self._trim(d) for d in self._crop_at_row(drawing, row))
        ordered_frames = tuple(
            frames[i] for i in self.sprite_sheet.style._frame_indices()
        )
        return CyclicAnimation(
            frames=ordered_frames, duration_per_frame=self.duration_per_frame
        )

    def _crop_at_row(self, drawing: Drawing, row: int) -> tuple[Drawing, ...]:
        num_frames = len(self.sprite_sheet.style)
        width = drawing.width.value / num_frames
        height = drawing.height.value / len(_DIR_TO_ROW)
        size = Size(width, height)
        return tuple(
            drawing.crop(
                RectangleAreaOnScreen(Coordinate(width * i, height * row), size)
            )
            for i in range(num_frames)
        )

    @property
    def _init_animation(self) -> dict[Direction, CyclicAnimation]:
        if self.selection:
            drawing = self.sprite_sheet.select(self.selection)
        else:
            drawing = self.sprite_sheet.drawing
        return {
            direction: self._load_row(drawing, row)
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
