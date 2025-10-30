from collections.abc import Callable
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import ClassVar, Self, override

from nextrpg.animation.cycle import Cycle
from nextrpg.animation.fade import FadeIn, FadeOut
from nextrpg.config.config import config
from nextrpg.config.widget.button_config import ButtonConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
    throw,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.text import Text
from nextrpg.event.io_event import IoEvent, KeyboardKey, is_key_press
from nextrpg.geometry.dimension import Size
from nextrpg.scene.scene import Scene
from nextrpg.widget.sizable_widget import (
    SizableWidget,
    SizableWidgetOnScreen,
)
from nextrpg.widget.widget import Widget


@dataclass_with_default(frozen=True, kw_only=True)
class ButtonOnScreen(SizableWidgetOnScreen):
    widget: Button

    @override
    @cached_property
    def drawing(self) -> AnimationLike:
        if self._is_selected:
            return self.widget.active
        return self.widget.idle

    @override
    def _event_after_selected(self, event: IoEvent) -> Scene:
        if not is_key_press(event, KeyboardKey.CONFIRM):
            return self

        if callable(self.widget.on_click):
            self.widget.on_click()
            return self

        if isinstance(self.widget.on_click, Widget):
            res = self.widget.on_click.widget_on_screen(
                self.name_to_on_screens, self.parent
            ).select
            return res

        return self.widget.on_click

    @override
    def _tick_without_parent_and_animation(
        self, time_delta: Millisecond
    ) -> Self:
        if self._is_selected:
            active = self.widget.active.tick(time_delta)
            idle = self.widget.idle
        else:
            active = self.widget.active
            idle = self.widget.idle.tick(time_delta)
        widget = replace(self.widget, idle=idle, active=active)
        return replace(self, widget=widget)


@dataclass_with_default(frozen=True, kw_only=True)
class Button(SizableWidget):
    on_click: Scene | Widget | Callable[[], None]
    idle: AnimationLike
    active: AnimationLike
    name: str | None = None
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = ButtonOnScreen

    @override
    @cached_property
    def size(self) -> Size:
        return self.idle.size


@dataclass_with_default(frozen=True, kw_only=True)
class DefaultButton(Button):
    text: str | AnimationLike = default(
        lambda self: self.name if self.name else throw("Require name or text.")
    )
    config: ButtonConfig = field(default_factory=lambda: config().widget.button)
    _: KW_ONLY = private_init_below()
    idle: AnimationLike = default(lambda self: self._init_idle)
    active: AnimationLike = default(lambda self: self._init_active)

    @property
    def _init_active(self) -> AnimationLike:
        padding = self.config.padding
        border_radius = self.config.border_radius
        background_border = self.idle.drawings[0].background(
            self.config.border_color,
            padding,
            border_radius,
            self.config.border_width,
        )
        background = self.idle.drawings[0].background(
            self.config.background_color, padding, border_radius
        )

        duration = self.config.fade_duration
        fade_in = FadeIn((background_border, background), duration)
        fade_out = FadeOut((background_border, background), duration)
        animation = Cycle((fade_out, fade_in))
        return DrawingGroup((animation, self.idle))

    @property
    def _init_idle(self) -> AnimationLike:
        if isinstance(self.text, str):
            return Text(self.text, self.config.text_config)
        return self.text
