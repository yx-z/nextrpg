from dataclasses import KW_ONLY
from typing import TYPE_CHECKING, override

from frozendict import frozendict

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.animation.animation_spec import AnimationSpec
from nextrpg.animation.fade import FadeIn, FadeOut
from nextrpg.config.menu_config import MenuConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.sprite_on_screen import animate_on_screen
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.widget.panel import Panel
from nextrpg.widget.panel_spec import PanelSpec

if TYPE_CHECKING:
    from nextrpg.map.map_scene import MapScene


@dataclass_with_default(frozen=True, kw_only=True)
class MenuScene(Panel):
    parent: MapScene
    config: MenuConfig
    _: KW_ONLY = private_init_below()
    spec: PanelSpec = default(lambda self: self.config.widget)
    name_to_on_screens: frozendict[str, Coordinate | AreaOnScreen] = default(
        lambda self: self.config.tmx.name_to_on_screens
    )
    background: DrawingOnScreen = default(
        lambda self: self._init_blurred_background
    )
    is_selected: bool = True
    _tick_parent: bool = False

    @override
    @property
    def _init_enter_animation(self) -> AnimationOnScreens:
        fade_in = animate_on_screen(
            self.background, FadeIn, duration=self.config.fade_duration
        )
        return self._init_animation(fade_in, self.spec.enter_animation)

    @override
    @property
    def _init_exit_animation(self) -> AnimationOnScreens:
        fade_out = animate_on_screen(
            self.background, FadeOut, duration=self.config.fade_duration
        )
        return self._init_animation(fade_out, self.spec.exit_animation)

    def _init_animation(
        self,
        background_animation: AnimationOnScreens,
        spec: AnimationSpec | None,
    ) -> AnimationOnScreens:
        if spec:
            widget_animation = spec.animate_on_screen(
                self.group_drawing_on_screens
            )
            return background_animation.concur(widget_animation)
        return background_animation

    @property
    def _init_blurred_background(self) -> DrawingOnScreen:
        return self.parent.drawing_on_screens.drawing_on_screen.blur(
            self.config.blur_radius
        )
