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
from nextrpg.core.tmx_loader import TmxLoader, get_coordinate, get_geometry
from nextrpg.draw.color import Color
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.scene.ui.widget_group import WidgetGroupOnScreen
from nextrpg.scene.view_only_scene import ViewOnlyScene


@dataclass_with_default(frozen=True, kw_only=True)
class TitleScene(WidgetGroupOnScreen):
    tmx_file: Path
    background: str | Color | DrawingOnScreen | AnimationOnScreen
    _: KW_ONLY = private_init_below()
    name_to_on_screens: dict[str, Coordinate | AreaOnScreen] = default(
        lambda self: self._init_name_to_on_screens
    )
    _is_selected: bool = True
    _background_scene: ViewOnlyScene = default(
        lambda self: self._init_background_scene
    )

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return (
            self._background_scene.drawing_on_screens
            + super().drawing_on_screens
        )

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        background_scene = self._background_scene.tick(time_delta)
        return replace(self, _background_scene=background_scene)

    @property
    def _init_background_scene(self) -> ViewOnlyScene:
        if isinstance(self.background, str):
            drawing = self._tmx.image_layer(self.background)
        else:
            drawing = self.background
        return ViewOnlyScene(drawing)

    @cached_property
    def _tmx(self) -> TmxLoader:
        return TmxLoader(self.tmx_file)

    @property
    def _init_name_to_on_screens(self) -> dict[str, Coordinate | AreaOnScreen]:
        name_to_on_screens: dict[str, Coordinate | AreaOnScreen] = {}
        for obj in self._tmx.all_objects:
            if isinstance(area := get_geometry(obj), AreaOnScreen):
                res = area
            else:
                res = get_coordinate(obj)
            name_to_on_screens[obj.name] = res
        return name_to_on_screens
