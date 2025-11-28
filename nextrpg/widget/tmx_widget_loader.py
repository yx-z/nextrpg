from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from frozendict import frozendict

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.core.cached_decorator import cached
from nextrpg.core.tmx_loader import TmxLoader, get_coordinate, get_geometry
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.sprite_on_screen import (
    SpriteOnScreen,
)
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate


@cached(lambda resource_config: resource_config.tmx_widget_loader_cache_size)
@dataclass(frozen=True)
class TmxWidgetLoader:
    tmx: Path | TmxLoader

    def background(
        self,
        background_layer: (
            str | SpriteOnScreen | tuple[str | SpriteOnScreen, ...]
        ),
    ) -> AnimationOnScreens:
        match background_layer:
            case str():
                resources = self._image_layer(background_layer)
            case tuple():
                resources = tuple(
                    self._image_layer(res) if isinstance(res, str) else res
                    for res in background_layer
                )
            case _:
                resources = background_layer
        return AnimationOnScreens(resources)

    @cached_property
    def name_to_on_screens(
        self,
    ) -> frozendict[str, Coordinate | AreaOnScreen]:
        name_to_on_screens: dict[str, Coordinate | AreaOnScreen] = {}
        for obj in self._tmx.all_objects:
            if isinstance(area := get_geometry(obj), AreaOnScreen):
                res = area
            else:
                res = get_coordinate(obj)
            name_to_on_screens[obj.name] = res
        return frozendict(name_to_on_screens)

    @cached_property
    def _tmx(self) -> TmxLoader:
        if isinstance(self.tmx, TmxLoader):
            return self.tmx
        return TmxLoader(self.tmx)

    def _image_layer(self, layer: str) -> DrawingOnScreen:
        return self._tmx.image_layer(layer)
