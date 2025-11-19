from frozendict import frozendict

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.tmx_loader import TmxLoader, get_coordinate, get_geometry
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.sprite_on_screen import (
    SpriteOnScreen,
)
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.widget.widget_group import WidgetGroupOnScreen


@dataclass_with_default(frozen=True, kw_only=True)
class TmxWidgetGroupOnScreen(WidgetGroupOnScreen):
    tmx: TmxLoader
    background_layer: (
        str | SpriteOnScreen | tuple[str | SpriteOnScreen, ...]
    ) = ()
    _ = private_init_below()
    background: SpriteOnScreen = default(lambda self: self._init_background)
    name_to_on_screens: dict[str, Coordinate | AreaOnScreen] = default(
        lambda self: self._init_name_to_on_screens
    )
    _is_selected: bool = True

    @property
    def _init_background(self) -> AnimationOnScreens:
        match self.background_layer:
            case str():
                resources = self._image_layer(self.background_layer)
            case tuple():
                resources = tuple(
                    self._image_layer(res) if isinstance(res, str) else res
                    for res in self.background_layer
                )
            case _:
                resources = self.background_layer
        return AnimationOnScreens(resources)

    def _image_layer(self, layer: str) -> DrawingOnScreen:
        return self.tmx.image_layer(layer)

    @property
    def _init_name_to_on_screens(
        self,
    ) -> frozendict[str, Coordinate | AreaOnScreen]:
        name_to_on_screens: dict[str, Coordinate | AreaOnScreen] = {}
        for obj in self.tmx.all_objects:
            if isinstance(area := get_geometry(obj), AreaOnScreen):
                res = area
            else:
                res = get_coordinate(obj)
            name_to_on_screens[obj.name] = res
        return frozendict(name_to_on_screens)
