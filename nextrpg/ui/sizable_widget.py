from abc import abstractmethod

from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.ui.widget import Widget


class SizableWidget[T](Widget[T]):
    coordinate: Coordinate | None = None

    @property
    @abstractmethod
    def size(self) -> Size: ...
