from dataclasses import dataclass
from functools import cached_property

from frozendict import frozendict

from nextrpg.core.tmx_loader import TmxLoader, get_coordinate, get_geometry
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate


@dataclass(frozen=True)
class WidgetLoader(TmxLoader):
    @cached_property
    def name_to_on_screens(self) -> frozendict[str, Coordinate | AreaOnScreen]:
        name_to_on_screens: dict[str, Coordinate | AreaOnScreen] = {}
        for obj in self.all_objects:
            if isinstance(area := get_geometry(obj), AreaOnScreen):
                res = area
            else:
                res = get_coordinate(obj)
            name_to_on_screens[obj.name] = res
        return frozendict(name_to_on_screens)
