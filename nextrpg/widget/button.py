from collections.abc import Callable
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import ClassVar, Self, override

from nextrpg import KeyMappingConfig
from nextrpg.animation.cycle import Cycle
from nextrpg.animation.fade import FadeIn, FadeOut
from nextrpg.config.config import config
from nextrpg.config.widget.button_config import ButtonConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.core.util import throw
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.text import Text
from nextrpg.event.io_event import IoEvent, is_key_press
from nextrpg.geometry.dimension import Size
from nextrpg.scene.scene import Scene
from nextrpg.widget.sizable_widget import (
    SizableWidget,
    SizableWidgetOnScreen,
)
from nextrpg.widget.widget import WidgetOnScreen


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
        if not is_key_press(event, KeyMappingConfig.confirm):
            return self

        if isinstance(res := self.widget.on_click(self), WidgetOnScreen):
            # on_click adds a widget.
            return res.select
        if isinstance(res, Scene):
            # on_click returns a new scene.
            return self.exit(res)
        # on_click has side effects but doesn't change the scene.
        return self

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
class Button(SizableWidget[ButtonOnScreen]):
    on_click: Callable[[ButtonOnScreen], WidgetOnScreen | Scene | None]
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
        backgrounds = (background_border, background)
        fade_in = FadeIn(backgrounds, duration)
        fade_out = FadeOut(backgrounds, duration)
        fades = (fade_out, fade_in)
        animation = Cycle(fades)
        return DrawingGroup((animation, self.idle))

    @property
    def _init_idle(self) -> AnimationLike:
        if isinstance(self.text, str):
            return Text(self.text, self.config.text_config)
        return self.text
