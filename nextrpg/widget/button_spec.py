from dataclasses import KW_ONLY, field
from functools import cached_property
from typing import Callable, ClassVar, override

from nextrpg.animation.cycle import Cycle
from nextrpg.animation.fade import FadeIn, FadeOut
from nextrpg.config.config import config
from nextrpg.config.widget.button_config import ButtonConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.drawing.color import Color
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.shifted_sprite import ShiftedSprite
from nextrpg.drawing.sprite import Sprite
from nextrpg.drawing.text import Text
from nextrpg.game.game_state import GameState
from nextrpg.geometry.padding import Padding, padding_for_both_sides
from nextrpg.geometry.size import Size
from nextrpg.widget.button import Button
from nextrpg.widget.sizable_widget_spec import SizableWidgetSpec
from nextrpg.widget.widget_interaction_result import WidgetInteractionResult


@dataclass_with_default(frozen=True, kw_only=True)
class BaseButtonSpec(SizableWidgetSpec[Button]):
    on_click: Callable[[Button, GameState], WidgetInteractionResult]
    idle: Sprite
    active: Sprite
    _: KW_ONLY = private_init_below()
    widget_type: ClassVar[type] = Button

    @override
    @cached_property
    def size(self) -> Size:
        return self.idle.size


@dataclass_with_default(frozen=True, kw_only=True)
class ButtonSpec(BaseButtonSpec):
    text: str | Sprite = default(lambda self: self.name)
    config: ButtonConfig = field(default_factory=lambda: config().widget.button)
    _: KW_ONLY = private_init_below()
    idle: Sprite = default(lambda self: self._init_idle)
    active: Sprite = default(lambda self: self._init_active)

    @cached_property
    def _border(self) -> ShiftedSprite:
        background_border = self._text.drawings[0].background(
            self.config.border_color,
            self._padding,
            self.config.border_radius,
            self.config.border_width,
        )
        return self._shift(background_border)

    @property
    def _init_active(self) -> Sprite:
        background = self._background(self.config.active_background_color)
        backgrounds = DrawingGroup((self._border, background))
        fade_in = FadeIn(backgrounds, self.config.fade_duration)
        fade_out = FadeOut(backgrounds, self.config.fade_duration)
        animation = Cycle((fade_in, fade_out))
        return DrawingGroup((self.idle, animation, self._shifted_text))

    @property
    def _init_idle(self) -> Sprite:
        background = self._background(self.config.idle_background_color)
        return DrawingGroup((self._border, background, self._shifted_text))

    @cached_property
    def _shifted_text(self) -> ShiftedSprite:
        return self._shift(self._text)

    def _shift(self, sprite: Sprite | ShiftedSprite) -> ShiftedSprite:
        return sprite + self._padding.top_left

    def _background(self, color: Color) -> ShiftedSprite:
        background = self._text.drawings[0].background(
            color, self._padding, self.config.border_radius
        )
        return self._shift(background)

    @cached_property
    def _text(self) -> Sprite:
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
