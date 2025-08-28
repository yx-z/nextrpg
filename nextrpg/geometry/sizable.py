from typing import TYPE_CHECKING, Protocol

from nextrpg.geometry.anchored_coodinate import (
    BottomCenterCoordinate,
    BottomLeftCoordinate,
    BottomRightCoordinate,
    CenterCoordinate,
    CenterLeftCoodinate,
    CenterRightCoordinate,
    TopCenterCoordinate,
    TopRightCoordinate,
)
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import (
    Height,
    Size,
    Width,
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
    def top_right(self) -> TopRightCoordinate:
        left, top = self.top_left
        return TopRightCoordinate(left + self.width.value, top)

    @property
    def bottom_left(self) -> BottomLeftCoordinate:
        left, top = self.top_left
        return BottomLeftCoordinate(left, top + self.height.value)

    @property
    def bottom_right(self) -> BottomRightCoordinate:
        left, top = self.top_left
        return BottomRightCoordinate(
            left + self.width.value, top + self.height.value
        )

    @property
    def top_center(self) -> TopCenterCoordinate:
        left, top = self.top_left
        return TopCenterCoordinate(left + self.width.value / 2, top)

    @property
    def bottom_center(self) -> BottomCenterCoordinate:
        left, top = self.top_left
        return BottomCenterCoordinate(
            left + self.width.value / 2, top + self.height.value
        )

    @property
    def center_left(self) -> CenterLeftCoodinate:
        left, top = self.top_left
        return CenterLeftCoodinate(left, top + self.height.value / 2)

    @property
    def center_right(self) -> CenterRightCoordinate:
        left, top = self.top_left
        return CenterRightCoordinate(
            left + self.width.value, top + self.height.value / 2
        )

    @property
    def center(self) -> CenterCoordinate:
        left, top = self.top_left
        return CenterCoordinate(
            left + self.width.value / 2, top + self.height.value / 2
        )
