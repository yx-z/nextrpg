from dataclasses import KW_ONLY, field
from typing import TYPE_CHECKING, override

from nextrpg.animation.fade import FadeIn
from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.config.config import config
from nextrpg.config.menu_config import MenuConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.scene.widget.tmx_widget_group_on_screen import (
    TmxWidgetGroupOnScreen,
)
from nextrpg.scene.widget.widget_group import WidgetGroupOnScreen

if TYPE_CHECKING:
    from nextrpg.scene.map.map_scene import MapScene


@dataclass_with_default(frozen=True, kw_only=True)
class MenuScene(TmxWidgetGroupOnScreen):
    map: MapScene
    config: MenuConfig = field(default_factory=lambda: config().menu)
    _: KW_ONLY = private_init_below()
    parent: MapScene = default(lambda self: self.map.stop_player)
    background: tuple[DrawingOnScreen, ...] = default(
        lambda self: self._init_blurred_background
    )
    _fade_in: FadeIn = default(
        lambda self: FadeIn(self.background, self.config.fade_duration)
    )
    _tick_parent: bool = False

    @override
    @property
    def _init_enter_animation(self) -> TimedAnimationOnScreens:
        fade_in = FadeIn(self.background, self.config.fade_duration)
        if self.widget.enter_animation:
            widget_drawing_on_screens = (
                WidgetGroupOnScreen._drawing_on_screens_after_parent.__get__(
                    self, WidgetGroupOnScreen
                )
            )
            animation = self.widget.enter_animation(widget_drawing_on_screens)
            return fade_in.concurrent(animation)
        return fade_in

    @property
    def _init_blurred_background(self) -> tuple[DrawingOnScreen, ...]:
        drawing_on_screens = DrawingOnScreens(self.parent.drawing_on_screens)
        blurred = drawing_on_screens.drawing_on_screen.blur(
            self.config.blur_radius
        )
        return (blurred,)
