from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import Enum, auto
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self, override

from pygame.locals import FULLSCREEN, RESIZABLE

from nextrpg.core.color import BLACK, Color
from nextrpg.core.dimension import Size
from nextrpg.core.save import UpdateFromSave

if TYPE_CHECKING:
    from nextrpg.draw.drawing import Drawing


class ResizeMode(Enum):
    SCALE = auto()
    KEEP_NATIVE_SIZE = auto()


@dataclass(frozen=True, slots=True)
class WindowConfig(UpdateFromSave[dict[str, Any]]):
    title: str = "nextrpg"
    size: Size = Size(1280, 720)
    background: Color = BLACK
    double_buffer: bool = True
    full_screen: bool = False
    resize: ResizeMode = ResizeMode.SCALE
    allow_resize: bool = True
    include_fps_in_window_title: bool = False
    icon_input: str | Path | Drawing | Callable[[], Drawing] | None = None

    @cached_property
    def icon(self) -> Drawing | None:
        if not self.icon_input:
            return None

        from nextrpg.draw.drawing import Drawing

        if callable(self.icon_input):
            return self.icon_input()
        if isinstance(self.icon_input, Drawing):
            return self.icon_input
        return Drawing(self.icon_input)

    def need_new_screen(self, other: WindowConfig) -> bool:
        return self.size != other.size or self.flag != other.flag

    @property
    @override
    def save_data(self) -> dict[str, Any]:
        return {"size": self.size.save_data, "full_screen": self.full_screen}

    @override
    def update(self, data: dict[str, Any]) -> Self:
        size = Size.load(data["size"])
        full_screen = data["full_screen"]
        return replace(self, size=size, full_screen=full_screen)

    @property
    def flag(self) -> _WindowFlag:
        flag = self.double_buffer
        if self.full_screen:
            flag |= FULLSCREEN
        if self.allow_resize:
            flag |= RESIZABLE
        return flag


type _WindowFlag = int
