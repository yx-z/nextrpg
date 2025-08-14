from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Self, override

from nextrpg.core.color import BLACK, Color
from nextrpg.core.dimension import Size
from nextrpg.core.save import LoadFromSave


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
class GuiConfig(LoadFromSave):
    title: str = "nextrpg"
    size: Size = Size(1280, 720)
    frames_per_second: int = 60
    background: Color = BLACK
    double_buffer: bool = True
    gui_mode: GuiMode = GuiMode.WINDOWED
    resize_mode: ResizeMode = ResizeMode.SCALE
    allow_window_resize: bool = True
    icon: Path | None = None

    @override
    def save(self) -> dict[str, Any]:
        return asdict(self) | {
            "gui_mode": self.gui_mode.name,
            "resize_mode": self.resize_mode.name,
        }

    @classmethod
    @override
    def load(cls, data: dict[str, Any]) -> Self:
        size_dict = data["size"]
        size = Size(size_dict["input_width"], size_dict["input_height"])
        background_dict = data["background"]
        color = Color(
            background_dict["red"],
            background_dict["green"],
            background_dict["blue"],
            background_dict["alpha"],
        )
        return GuiConfig(
            data["title"],
            size,
            data["frames_per_second"],
            color,
            data["double_buffer"],
            GuiMode[data["gui_mode"]],
            ResizeMode[data["resize_mode"]],
            data["allow_window_resize"],
            Path(data["icon"]) if data["icon"] else None,
        )


_OPPOSITE_GUI_MODE = {
    GuiMode.WINDOWED: GuiMode.FULL_SCREEN,
    GuiMode.FULL_SCREEN: GuiMode.WINDOWED,
}
