from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from itertools import cycle
from pathlib import Path

from pygame import Surface
from pygame.image import load

from nextrpg.common_types import CharacterSprite, Direction, Millesecond


class DefaultFrameType(IntEnum):
    RIGHT = 0
    IDLE = 1
    LEFT = 2

    @classmethod
    def frame_sequence(cls) -> Iterable[int]:
        return cycle(
            [
                DefaultFrameType.IDLE,
                DefaultFrameType.RIGHT,
                DefaultFrameType.IDLE,
                DefaultFrameType.LEFT,
            ]
        )


class XpFrameType(IntEnum):
    IDLE = 0
    RIGHT = 1
    IDLE_AGAIN = 2
    LEFT = 3

    @classmethod
    def frame_sequence(cls) -> Iterable[int]:
        return cycle(cls)


class Style(Enum):
    DEFAULT = auto()
    XP = auto()

    @property
    def frame_type(self) -> type[DefaultFrameType] | type[XpFrameType]:
        return {Style.DEFAULT: DefaultFrameType, Style.XP: XpFrameType}[self]


@dataclass(frozen=True)
class SpriteSheetSelection:
    row: int
    col: int
    max_rows: int = 2
    max_cols: int = 4


@dataclass(frozen=True)
class SpriteSheet:
    sprite_sheet: Path
    selection: SpriteSheetSelection | None = None
    style: Style = Style.DEFAULT


class Frames:
    def __init__(
        self,
        frame_sequence: Iterable[int],
        frames: list[Surface],
    ) -> None:
        self.frame_sequence = frame_sequence
        self.frames = frames
        self.current_frame_index = next(frame_sequence)

    def current_frame(self) -> Surface:
        return self.frames[self.current_frame_index]

    def next_frame(self) -> Surface:
        self.current_frame_index = next(self.frame_sequence)
        return self.frames[self.current_frame_index]


def crop_into_frames_at_row(
    image: Surface, row: int, style: Style
) -> list[Surface]:
    width = image.width / len(style.frame_type)
    height = image.height / len(Direction)
    return [
        image.subsurface((width * i, height * row, width, height))
        for i in range(len(style.frame_type))
    ]


def crop_image_by_selection(
    image: Surface, selection: SpriteSheetSelection
) -> Surface:
    width = image.width / selection.max_cols
    height = image.height / selection.max_rows
    return image.subsurface(
        (width * selection.col, height * selection.row, width, height)
    )


def load_sprite_frames(
    sprite_sheet: SpriteSheet,
) -> dict[Direction, Frames]:
    image = load(sprite_sheet.sprite_sheet)
    if sprite_sheet.selection:
        image = crop_image_by_selection(image, sprite_sheet.selection)
    return {
        direction: Frames(
            sprite_sheet.style.frame_type.frame_sequence(),
            crop_into_frames_at_row(image, row, sprite_sheet.style),
        )
        for direction, row in {
            Direction.DOWN: 0,
            Direction.LEFT: 1,
            Direction.RIGHT: 2,
            Direction.UP: 3,
        }.items()
    }


class RpgMakerCharacterSprite(CharacterSprite):
    def __init__(
        self,
        sprite_sheet: SpriteSheet,
        animate_on_idle: bool = False,
        frame_duration: Millesecond = Millesecond(100),
    ) -> None:
        self.sprite_frames = load_sprite_frames(sprite_sheet)
        self.animate_on_idle = animate_on_idle
        self.frame_duration = frame_duration
        self.frame_time = Millesecond(0)

    def draw(self, time_delta: Millesecond, direction: Direction) -> Surface:
        if self.frame_time > self.frame_duration:
            self.frame_time = Millesecond(0)
            return self.sprite_frames[direction].next_frame()
        self.frame_time += time_delta
        return self.sprite_frames[direction].current_frame()
