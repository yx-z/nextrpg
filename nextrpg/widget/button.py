from collections.abc import Callable
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import ClassVar, Self, override

from nextrpg.animation.cycle import Cycle
from nextrpg.animation.fade import FadeIn, FadeOut
from nextrpg.config.config import config
from nextrpg.config.system.key_mapping_config import KeyMappingConfig
from nextrpg.config.widget.button_config import ButtonConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.core.util import throw
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.sprite import Sprite
from nextrpg.drawing.text import Text
from nextrpg.drawing.text_group import TextGroup
from nextrpg.event.io_event import IoEvent, is_key_press
from nextrpg.game.game_state import GameState
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.padding import (
    Padding,
    padding_for_both_sides,
)
from nextrpg.scene.scene import Scene
from nextrpg.widget.sizable_widget import (
    SizableWidget,
    SizableWidgetOnScreen,
)
from nextrpg.widget.widget import WidgetOnScreen


@dataclass_with_default(frozen=True, kw_only=True)
class ButtonOnScreen(SizableWidgetOnScreen):
    widget: BaseButton

    @override
    @cached_property
    def drawing(self) -> Sprite:
        if self._is_selected:
            return self.widget.active
        return self.widget.idle

    @override
    def _event_after_selected(
        self, event: IoEvent, state: GameState
    ) -> tuple[Scene, GameState]:
        if not is_key_press(event, KeyMappingConfig.confirm):
            return self, state

        if isinstance(res := self.widget.on_click(self, state), tuple):
            res, state = res
        match res:
            case WidgetOnScreen():
                return res.select, state
            case Scene():
                return self.exit(res), state
        return self, state

    @override
    def _tick_without_parent_and_animation(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Self, GameState]:
        if self._is_selected:
            active = self.widget.active.tick(time_delta)
            idle = self.widget.idle
        else:
            active = self.widget.active
            idle = self.widget.idle.tick(time_delta)
        widget = replace(self.widget, idle=idle, active=active)
        ticked = replace(self, widget=widget)
        return ticked, state


OnClickSceneResult = WidgetOnScreen | Scene | None
OnClickResult = OnClickSceneResult | tuple[OnClickSceneResult, GameState]


@dataclass_with_default(frozen=True, kw_only=True)
class BaseButton(SizableWidget[ButtonOnScreen]):
    on_click: Callable[[ButtonOnScreen, GameState], OnClickResult]
    idle: Sprite
    active: Sprite
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = ButtonOnScreen

    @override
    @cached_property
    def size(self) -> Size:
        return self.idle.size


@dataclass_with_default(frozen=True, kw_only=True)
class Button(BaseButton):
    text: str | Text | TextGroup = default(
        lambda self: self.name if self.name else throw("Require name or text.")
    )
    config: ButtonConfig = field(default_factory=lambda: config().widget.button)
    _: KW_ONLY = private_init_below()
    idle: Sprite = default(lambda self: self._shift(self._text))
    active: Sprite = default(lambda self: self._init_active)

    @property
    def _init_active(self) -> Sprite:
        background_border = self._text.drawings[0].background(
            self.config.border_color,
            self._padding,
            self.config.border_radius,
            self.config.border_width,
        )
        background = self._text.drawings[0].background(
            self.config.background_color,
            self._padding,
            self.config.border_radius,
        )

        background_group = DrawingGroup((background_border, background))
        backgrounds = background_group + self._padding.top_left
        fade_in = FadeIn(backgrounds, self.config.fade_duration)
        fade_out = FadeOut(backgrounds, self.config.fade_duration)
        animation = Cycle((fade_out, fade_in))
        return DrawingGroup((animation, self.idle))

    def _shift(self, resource: Sprite) -> Sprite:
        shifted = resource + self._padding.top_left.size
        return DrawingGroup(shifted)

    @cached_property
    def _text(self) -> Text | TextGroup:
        if isinstance(self.text, str):
            return Text(self.text, self.config.text_config)
        return self.text

    @cached_property
    def _padding(self) -> Padding:
        if isinstance(self.config.padding_or_size, Padding):
            return self.config.padding_or_size
        button_size = self.config.padding_or_size
        width = (button_size.width - self._text.width) / 2
        height = (button_size.height - self._text.height) / 2
        return padding_for_both_sides(width, height)
