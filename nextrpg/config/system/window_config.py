from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Any, Self, override

from pygame import DOUBLEBUF, FULLSCREEN, HWSURFACE, RESIZABLE

from nextrpg.core.save import UpdateSavable
from nextrpg.drawing.color import BLACK, Color
from nextrpg.drawing.sprite import Sprite
from nextrpg.geometry.size import Size


@dataclass(frozen=True)
class WindowConfig(UpdateSavable[dict[str, Any]]):
    title: str = "nextrpg"
    size: Size = Size(1280, 720)
    background: Color = BLACK
    double_buffer: bool = True
    full_screen: bool = False
    allow_resize: bool = True
    include_fps_in_window_title: bool = False
    hardware_surface: bool = True
    icon_input: Sprite | Callable[[], Sprite] | None = None

    @cached_property
    def icon(self) -> Sprite | None:
        if self.icon_input is None:
            return None
        if callable(self.icon_input):
            return self.icon_input()
        return self.icon_input

    def need_new_screen(self, other: WindowConfig) -> bool:
        return self.size != other.size or self.flag != other.flag

    @override
    @cached_property
    def save_data_this_class(self) -> dict[str, Any]:
        return {"size": self.size.save_data, "full_screen": self.full_screen}

    @override
    def update_this_class_from_save(self, data: dict[str, Any]) -> Self:
        size = Size.load_from_save(data["size"])
        full_screen = data["full_screen"]
        return replace(self, size=size, full_screen=full_screen)

    @cached_property
    def flag(self) -> _WindowFlag:
        flag = 0
        if self.hardware_surface:
            flag |= HWSURFACE
        if self.double_buffer:
            flag |= DOUBLEBUF
        if self.full_screen:
            flag |= FULLSCREEN
        if self.allow_resize:
            flag |= RESIZABLE
        return flag


type _WindowFlag = int
