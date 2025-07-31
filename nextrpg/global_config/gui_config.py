from dataclasses import dataclass
from enum import Enum, auto

from nextrpg.core.color import BLACK, Color
from nextrpg.core.dimension import Size


class ResizeMode(Enum):
    SCALE = auto()
    KEEP_NATIVE_SIZE = auto()


class GuiMode(Enum):
    WINDOWED = auto()
    FULL_SCREEN = auto()

    @property
    def opposite(self) -> GuiMode:
        return _OPPOSITE_GUI_MODE[self]


@dataclass(frozen=True)
class GuiConfig:
    title: str = "nextrpg"
    size: Size = Size(1280, 720)
    frames_per_second: int = 60
    background: Color = BLACK
    double_buffer: bool = True
    gui_mode: GuiMode = GuiMode.WINDOWED
    resize_mode: ResizeMode = ResizeMode.SCALE
    allow_window_resize: bool = True


_OPPOSITE_GUI_MODE = {
    GuiMode.WINDOWED: GuiMode.FULL_SCREEN,
    GuiMode.FULL_SCREEN: GuiMode.WINDOWED,
}
