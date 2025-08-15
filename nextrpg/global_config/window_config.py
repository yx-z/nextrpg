from __future__ import annotations

from dataclasses import dataclass, replace
from enum import auto
from pathlib import Path
from typing import Any, Self, override

from pygame.locals import FULLSCREEN, RESIZABLE

from nextrpg.core.color import BLACK, Color
from nextrpg.core.dimension import Size
from nextrpg.core.save import LoadFromSaveEnum, UpdateFromSave


class ResizeMode(LoadFromSaveEnum):
    SCALE = auto()
    KEEP_NATIVE_SIZE = auto()


class WindowMode(LoadFromSaveEnum):
    WINDOWED = auto()
    FULL_SCREEN = auto()

    @property
    def opposite(self) -> WindowMode:
        return _OPPOSITE_GUI_MODE[self]


type WindowFlag = int


@dataclass(frozen=True)
class WindowConfig(UpdateFromSave[dict[str, Any]]):
    title: str = "nextrpg"
    size: Size = Size(1280, 720)
    frames_per_second: int = 60
    background: Color = BLACK
    double_buffer: bool = True
    mode: WindowMode = WindowMode.WINDOWED
    resize: ResizeMode = ResizeMode.SCALE
    allow_resize: bool = True
    icon: str | Path | None = None

    @property
    @override
    def save_data(self) -> dict[str, Any]:
        return {"size": self.size.save_data, "mode": self.mode.save_data}

    @override
    def update(self, data: dict[str, Any]) -> Self:
        size = Size.load(data["size"])
        mode = WindowMode.load(data["mode"])
        return replace(self, size=size, mode=mode)

    @property
    def flag(self) -> WindowFlag:
        flag = self.double_buffer
        if self.mode is WindowMode.FULL_SCREEN:
            flag |= FULLSCREEN
        if self.allow_resize:
            flag |= RESIZABLE
        return flag


_OPPOSITE_GUI_MODE = {
    WindowMode.WINDOWED: WindowMode.FULL_SCREEN,
    WindowMode.FULL_SCREEN: WindowMode.WINDOWED,
}
