from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum, auto
from typing import override

from nextrpg.core.color import BLACK, Color
from nextrpg.core.dimension import Size
from nextrpg.save.json_saveable import Json, JsonSaveable


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
class GuiConfig(JsonSaveable):
    @override
    @property
    def save(self) -> Json:
        return asdict(self) | {
            "gui_mode": self.gui_mode.name,
            "resize_mode": self.resize_mode.name,
        }

    @override
    def load(self, data: Json) -> GuiConfig:
        size_dict = data["size"]
        size = Size(size_dict["input_width"], size_dict["input_height"])
        return GuiConfig(
            data["title"],
            size,
            data["frames_per_second"],
            Color(*data["background"]),
            data["double_buffer"],
            GuiMode[data["gui_mode"]],
            ResizeMode[data["resize_mode"]],
            data["allow_window_resize"],
        )

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
