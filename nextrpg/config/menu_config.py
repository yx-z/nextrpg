from collections.abc import Callable
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from nextrpg.core.time import Millisecond
from nextrpg.drawing.sprite import BlurRadius

if TYPE_CHECKING:
    from nextrpg.widget.panel_spec import PanelSpec
    from nextrpg.widget.widget_loader import WidgetLoader


@dataclass(frozen=True)
class MenuConfig:
    widget_input: PanelSpec | Callable[[], PanelSpec]
    tmx_input: WidgetLoader | Callable[[], WidgetLoader]
    blur_radius: BlurRadius = 2
    fade_duration_override: Millisecond | None = None

    @cached_property
    def widget(self) -> PanelSpec:
        if callable(self.widget_input):
            return self.widget_input()
        return self.widget_input

    @cached_property
    def tmx(self) -> WidgetLoader:
        if callable(self.tmx_input):
            return self.tmx_input()
        return self.tmx_input

    @cached_property
    def fade_duration(self) -> Millisecond:
        from nextrpg.config.config import config

        if self.fade_duration_override is not None:
            return self.fade_duration_override
        return config().animation.default_timed_animation_duration
