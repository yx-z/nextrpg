from collections.abc import Callable
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from nextrpg.core.time import Millisecond

if TYPE_CHECKING:
    from nextrpg.core.tmx_loader import TmxLoader
    from nextrpg.widget.widget_group import WidgetGroup


@dataclass(frozen=True)
class MenuConfig:
    widget_input: Callable[[], WidgetGroup]
    tmx_input: TmxLoader | Callable[[], TmxLoader]
    blur_radius: int = 2
    fade_duration_override: Millisecond | None = None

    @cached_property
    def widget(self) -> WidgetGroup:
        return self.widget_input()

    @cached_property
    def tmx(self) -> TmxLoader:
        if callable(self.tmx_input):
            return self.tmx_input()
        return self.tmx_input

    @cached_property
    def fade_duration(self) -> Millisecond:
        from nextrpg.config.config import config

        if self.fade_duration_override is not None:
            return self.fade_duration_override
        return config().timing.animation_duration
