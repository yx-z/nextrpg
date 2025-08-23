from dataclasses import dataclass

from nextrpg.core.coordinate import ORIGIN, Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.sizable import Sizable


@dataclass(frozen=True)
class SizableArea(Sizable):
    size: Size
    top_left: Coordinate = ORIGIN
