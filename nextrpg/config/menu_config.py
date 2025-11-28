from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING, Any

from nextrpg.core.time import Millisecond
from nextrpg.drawing.sprite import BlurRadius

if TYPE_CHECKING:
    from nextrpg.widget.tmx_widget_loader import TmxWidgetLoader
    from nextrpg.widget.widget_group import WidgetGroup


@dataclass(frozen=True)
class MenuConfig:
    widget_input: Callable[[], WidgetGroup]
    tmx_input: TmxWidgetLoader | Callable[[], TmxWidgetLoader]
    blur_radius: BlurRadius = 2
    fade_duration_override: Millisecond | None = None
    kwargs_input: dict[str, Any] | Callable[[], dict[str, Any]] = field(
        default_factory=dict
    )

    @cached_property
    def kwargs(self) -> dict[str, Any]:
        if callable(self.kwargs_input):
            return self.kwargs_input()
        return self.kwargs_input

    @cached_property
    def widget(self) -> WidgetGroup:
        return self.widget_input()

    @cached_property
    def tmx(self) -> TmxWidgetLoader:
        if callable(self.tmx_input):
            return self.tmx_input()
        return self.tmx_input

    @cached_property
    def fade_duration(self) -> Millisecond:
        from nextrpg.config.config import config

        if self.fade_duration_override is not None:
            return self.fade_duration_override
        return config().animation.default_timed_animation_duration
