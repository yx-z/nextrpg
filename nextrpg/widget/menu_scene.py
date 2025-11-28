from dataclasses import KW_ONLY, field
from typing import TYPE_CHECKING, override

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.animation.fade import FadeIn, FadeOut
from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.animation.timed_animation_spec import TimedAnimationSpec
from nextrpg.config.config import config
from nextrpg.config.menu_config import MenuConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.drawing.sprite_on_screen import animate
from nextrpg.widget.widget_group import WidgetGroupOnScreen

if TYPE_CHECKING:
    from nextrpg.map.map_scene import MapScene


@dataclass_with_default(frozen=True, kw_only=True)
class MenuScene(WidgetGroupOnScreen):
    parent: MapScene
    config: MenuConfig = field(default_factory=lambda: config().menu)
    is_selected: bool = True
    _: KW_ONLY = private_init_below()
    background: DrawingOnScreen = default(
        lambda self: self._init_blurred_background
    )
    _tick_parent: bool = False

    @override
    @property
    def _init_enter_animation(self) -> AnimationOnScreens:
        fade_in = animate(
            self.background, FadeIn, duration=self.config.fade_duration
        )
        return self._init_animation(fade_in, self.widget.enter_animation)

    @override
    @property
    def _init_exit_animation(self) -> AnimationOnScreens:
        fade_out = animate(
            self.background, FadeOut, duration=self.config.fade_duration
        )
        return self._init_animation(fade_out, self.widget.exit_animation)

    def _init_animation(
        self,
        background_animation: TimedAnimationOnScreens,
        spec: TimedAnimationSpec | None,
    ) -> AnimationOnScreens:
        if spec:
            widget_animation = spec.animate(self.children_drawing_on_screens)
            return background_animation.concur(widget_animation)
        return background_animation

    @property
    def _init_blurred_background(self) -> DrawingOnScreen:
        drawing_on_screens = DrawingOnScreens(self.parent.drawing_on_screens)
        return drawing_on_screens.drawing_on_screen.blur(
            self.config.blur_radius
        )
