from functools import cached_property
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.anchored_coordinate import (
    BottomCenterCoordinate,
    BottomLeftCoordinate,
    BottomRightCoordinate,
    CenterCoordinate,
    CenterLeftCoodinate,
    CenterRightCoordinate,
    TopCenterCoordinate,
    TopRightCoordinate,
)
from nextrpg.geometry.coordinate import Coordinate, XAxis, YAxis
from nextrpg.geometry.size import Height, Size, Width

if TYPE_CHECKING:
    from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen


@runtime_checkable
class Sizable(Protocol):
    # Subclass shall implement these.
    size: Size
    top_left: Coordinate

    @cached_property
    def rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        from nextrpg.geometry.rectangle_area_on_screen import (
            RectangleAreaOnScreen,
        )

        return RectangleAreaOnScreen(self.top_left, self.size)

    @cached_property
    def width(self) -> Width:
        return self.size.width

    @cached_property
    def height(self) -> Height:
        return self.size.height

    @cached_property
    def top(self) -> YAxis:
        return self.top_left.top

    @cached_property
    def left(self) -> XAxis:
        return self.top_left.left

    @cached_property
    def bottom(self) -> YAxis:
        return self.top_left.top + self.size.height

    @cached_property
    def right(self) -> XAxis:
        return self.top_left.left + self.size.width

    @cached_property
    def top_right(self) -> TopRightCoordinate:
        left, top = self.top_left
        return TopRightCoordinate(left + self.width.value, top)

    @cached_property
    def bottom_left(self) -> BottomLeftCoordinate:
        left, top = self.top_left
        return BottomLeftCoordinate(left, top + self.height.value)

    @cached_property
    def bottom_right(self) -> BottomRightCoordinate:
        left, top = self.top_left
        return BottomRightCoordinate(
            left + self.width.value, top + self.height.value
        )

    @cached_property
    def top_center(self) -> TopCenterCoordinate:
        left, top = self.top_left
        return TopCenterCoordinate(left + self.width.value / 2, top)

    @cached_property
    def bottom_center(self) -> BottomCenterCoordinate:
        left, top = self.top_left
        return BottomCenterCoordinate(
            left + self.width.value / 2, top + self.height.value
        )

    @cached_property
    def center_left(self) -> CenterLeftCoodinate:
        left, top = self.top_left
        return CenterLeftCoodinate(left, top + self.height.value / 2)

    @cached_property
    def center_right(self) -> CenterRightCoordinate:
        left, top = self.top_left
        return CenterRightCoordinate(
            left + self.width.value, top + self.height.value / 2
        )

    @cached_property
    def center(self) -> CenterCoordinate:
        left, top = self.top_left
        return CenterCoordinate(
            left + self.width.value / 2, top + self.height.value / 2
        )

    def at_anchor(self, anchor: Anchor) -> Coordinate:
        match anchor:
            case Anchor.TOP_LEFT:
                return self.top_left
            case Anchor.TOP_CENTER:
                return self.top_center
            case Anchor.TOP_RIGHT:
                return self.top_right
            case Anchor.CENTER_LEFT:
                return self.center_left
            case Anchor.CENTER:
                return self.center
            case Anchor.CENTER_RIGHT:
                return self.center_right
            case Anchor.BOTTOM_LEFT:
                return self.bottom_left
            case Anchor.BOTTOM_CENTER:
                return self.bottom_center
            case Anchor.BOTTOM_RIGHT:
                return self.bottom_right
