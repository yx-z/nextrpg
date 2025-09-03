from abc import abstractmethod

from nextrpg.geometry.dimension import Size
from nextrpg.ui.widget import Widget


class SizableWidget[T](Widget[T]):
    @property
    @abstractmethod
    def size(self) -> Size: ...
