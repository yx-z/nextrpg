from dataclasses import replace
from functools import cached_property
from pathlib import Path
from typing import Self, override

from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.animation.animation_on_screens import AnimationOnScreens
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
from nextrpg.scene.ui.widget_group import WidgetGroupOnScreen


@dataclass_with_default(frozen=True, kw_only=True)
class TmxWidgets(WidgetGroupOnScreen):
    tmx: Path
    background: (
        str
        | DrawingOnScreen
        | AnimationOnScreen
        | tuple[str | DrawingOnScreen | AnimationOnScreen, ...]
        | None
    ) = None
    _ = private_init_below()
    name_to_on_screens: dict[str, Coordinate | AreaOnScreen] = default(
        lambda self: self._init_name_to_on_screens
    )
    is_selected: bool = True
    _background: AnimationOnScreens | None = default(
        lambda self: self._init_background
    )

    @override
    @cached_property
    def drawing_on_screens_after_parent(self) -> tuple[DrawingOnScreen, ...]:
        if self._background:
            return (
                self._background.drawing_on_screens
                + super().drawing_on_screens_after_parent
            )
        return super().drawing_on_screens_after_parent

    @override
    def tick_after_parent(self, time_delta: Millisecond) -> Self:
        if self._background:
            background = self._background.tick(time_delta)
        else:
            background = None
        return replace(self, _background=background)

    @property
    def _init_background(self) -> AnimationOnScreens | None:
        match self.background:
            case None:
                return None
            case str():
                drawing = (self._image_layer(self.background),)
            case tuple():
                drawing = tuple(
                    (self._image_layer(res) if isinstance(res, str) else res)
                    for res in self.background
                )
            case _:
                drawing = (self.background,)
        return AnimationOnScreens(drawing)

    def _image_layer(self, layer: str) -> DrawingOnScreen:
        return self._tmx.image_layer(layer)

    @cached_property
    def _tmx(self) -> TmxLoader:
        return TmxLoader(self.tmx)

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
