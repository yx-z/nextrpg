from dataclasses import KW_ONLY, replace
from functools import cached_property
from pathlib import Path
from typing import Self, override

from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.core.tmx_loader import TmxLoader, get_coordinate
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent
from nextrpg.scene.scene import Scene
from nextrpg.ui.selectable_widget_group import SelectableWidgetGroup
from nextrpg.ui.selectable_widget_group_on_screen import (
    SelectableWidgetGroupOnScreen,
)


@dataclass_with_default(frozen=True)
class TitleScene(Scene):
    tmx_file: Path
    background: str | DrawingOnScreen | AnimationOnScreen
    widget: SelectableWidgetGroup
    _: KW_ONLY = private_init_below()
    _widget_on_screen: SelectableWidgetGroupOnScreen = default(
        lambda self: self._init_selectable_widget_group_on_screen
    )
    _tmx: TmxLoader = default(lambda self: TmxLoader(self.tmx_file))

    @override
    def event(self, event: IoEvent) -> Self:
        widget_on_screen = self._widget_on_screen.event(event)
        return replace(self, _widget_on_screen=widget_on_screen)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        widget_on_screen = self._widget_on_screen.tick(time_delta)
        if isinstance(self.background, AnimationOnScreen):
            background = self.background.tick(time_delta)
        else:
            background = self.background
        return replace(
            self, background=background, _widget_on_screen=widget_on_screen
        )

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return self._background + self._widget_on_screen.drawing_on_screens

    @cached_property
    def _background(self) -> tuple[DrawingOnScreen, ...]:
        if isinstance(self.background, str):
            return (self._tmx.image_layer(self.background),)
        if isinstance(self.background, AnimationOnScreen):
            return self.background.drawing_on_screens
        return (self.background,)

    @cached_property
    def _init_selectable_widget_group_on_screen(
        self,
    ) -> SelectableWidgetGroupOnScreen:
        on_screen = {
            widget.unique_name: get_coordinate(
                self._tmx.get_object(widget.unique_name)
            )
            for widget in self.widget.widgets
        }
        return SelectableWidgetGroupOnScreen(self.widget, on_screen)
