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
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.scene.scene import Scene
from nextrpg.scene.ui.widget import Widget


@dataclass_with_default(frozen=True, kw_only=True)
class TitleScene(Scene):
    tmx_file: Path
    background: str | DrawingOnScreen | AnimationOnScreen
    _: KW_ONLY = private_init_below()
    _tmx: TmxLoader = default(lambda self: TmxLoader(self.tmx_file))

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if isinstance(self.background, AnimationOnScreen):
            background = self.background.tick(time_delta)
        else:
            background = self.background
        return replace(self, background=background)

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if isinstance(self.background, str):
            return (self._tmx.image_layer(self.background),)
        if isinstance(self.background, AnimationOnScreen):
            return self.background.drawing_on_screens
        return (self.background,)

    @cached_property
    def name_to_on_screens(self) -> dict[str, Coordinate | AreaOnScreen]:
        name_to_on_screens: dict[str, Coordinate | AreaOnScreen] = {}
        for obj in self._tmx.all_objects:
            if isinstance(area := get_geometry(obj), AreaOnScreen):
                res = area
            else:
                res = get_coordinate(obj)
            name_to_on_screens[obj.name] = res
        return name_to_on_screens


def title(
    tmx_file: Path,
    background: str | DrawingOnScreen | AnimationOnScreen,
    widget: Widget,
) -> Scene:
    title_scene = TitleScene(tmx_file=tmx_file, background=background)
    return (
        widget.widget_on_screen(title_scene.name_to_on_screens)
        .with_parent(title_scene)
        .select
    )
