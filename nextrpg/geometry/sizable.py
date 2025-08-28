from typing import Protocol, TYPE_CHECKING

from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import (
    Height,
    HeightScaling,
    Size,
    Width,
    WidthAndHeightScaling,
    WidthScaling,
)

if TYPE_CHECKING:
    from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen


class Sizable(Protocol):
    # Subclass shall implement these.
    size: Size
    top_left: Coordinate

    @property
    def rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        from nextrpg.geometry.rectangle_area_on_screen import (
            RectangleAreaOnScreen,
        )

        return RectangleAreaOnScreen(self.top_left, self.size)

    @property
    def width(self) -> Width:
        return self.size.width

    @property
    def height(self) -> Height:
        return self.size.height

    @property
    def top(self) -> Height:
        return self.top_left.top

    @property
    def left(self) -> Width:
        return self.top_left.left

    @property
    def bottom(self) -> Height:
        return self.top_left.top + self.size.height

    @property
    def right(self) -> Width:
        return self.top_left.left + self.size.width

    @property
    def top_right(self) -> Coordinate:
        return self.top_left + self.width

    @property
    def bottom_left(self) -> Coordinate:
        return self.top_left + self.height

    @property
    def bottom_right(self) -> Coordinate:
        return self.top_left + self.size

    @property
    def top_center(self) -> Coordinate:
        return self.top_left + self.width / 2

    @property
    def bottom_center(self) -> Coordinate:
        return self.top_left + self.size / WidthScaling(2)

    @property
    def center_left(self) -> Coordinate:
        return self.top_left + self.height / 2

    @property
    def center_right(self) -> Coordinate:
        return self.top_left + self.size / HeightScaling(2)

    @property
    def center(self) -> Coordinate:
        return self.top_left + self.size / WidthAndHeightScaling(2)
