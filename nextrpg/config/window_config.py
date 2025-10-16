from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Any, Self, override

from pygame import DOUBLEBUF
from pygame.locals import FULLSCREEN, RESIZABLE

from nextrpg.core.save import UpdateFromSave
from nextrpg.drawing.color import BLACK, Color
from nextrpg.geometry.dimension import Size

if TYPE_CHECKING:
    from nextrpg.drawing.drawing import Drawing


@dataclass(frozen=True)
class WindowConfig(UpdateFromSave[dict[str, Any]]):
    title: str = "nextrpg"
    size: Size = Size(1280, 720)
    background: Color = BLACK
    double_buffer: bool = True
    full_screen: bool = False
    allow_resize: bool = True
    include_fps_in_window_title: bool = False
    icon_input: Drawing | Callable[[], Drawing] | None = None

    @cached_property
    def icon(self) -> Drawing | None:
        if self.icon_input is None:
            return None
        if callable(self.icon_input):
            return self.icon_input()
        return self.icon_input

    def need_new_screen(self, other: WindowConfig) -> bool:
        return self.size != other.size or self.flag != other.flag

    @override
    @cached_property
    def save_data(self) -> dict[str, Any]:
        return {
            Size.save_key(): self.size.save_data,
            "full_screen": self.full_screen,
        }

    @override
    def update_from_save(self, data: dict[str, Any]) -> Self:
        size_key = Size.save_key()
        size = Size.load_from_save(data[size_key])
        full_screen = data["full_screen"]
        return replace(self, size=size, full_screen=full_screen)

    @cached_property
    def flag(self) -> _WindowFlag:
        flag = 0
        if self.double_buffer:
            flag |= DOUBLEBUF
        if self.full_screen:
            flag |= FULLSCREEN
        if self.allow_resize:
            flag |= RESIZABLE
        return flag


type _WindowFlag = int
