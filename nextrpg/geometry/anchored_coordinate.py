from typing import TYPE_CHECKING, override

from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.size import Size

if TYPE_CHECKING:
    from nextrpg.geometry.sizable import Sizable
    from nextrpg.geometry.sizable_proxy import (
        BottomCenterSizable,
        BottomLeftSizable,
        BottomRightSizable,
        CenterLeftSizable,
        CenterRightSizable,
        CenterSizable,
        TopCenterSizable,
        TopRightSizable,
    )


class TopCenterCoordinate(Coordinate):
    @override
    def as_top_left_of(self, size: Size | Sizable) -> TopCenterSizable:
        return self.as_top_center_of(size)


class TopRightCoordinate(Coordinate):
    @override
    def as_top_left_of(self, size: Size | Sizable) -> TopRightSizable:
        return self.as_top_right_of(size)


class CenterLeftCoodinate(Coordinate):
    @override
    def as_top_left_of(self, size: Size | Sizable) -> CenterLeftSizable:
        return self.as_center_left_of(size)


class CenterCoordinate(Coordinate):
    @override
    def as_top_left_of(self, size: Size | Sizable) -> CenterSizable:
        return self.as_center_of(size)


class CenterRightCoordinate(Coordinate):
    @override
    def as_top_left_of(self, size: Size | Sizable) -> CenterRightSizable:
        return self.as_center_right_of(size)


class BottomLeftCoordinate(Coordinate):
    @override
    def as_top_left_of(self, size: Size | Sizable) -> BottomLeftSizable:
        return self.as_bottom_left_of(size)


class BottomCenterCoordinate(Coordinate):
    @override
    def as_top_left_of(self, size: Size | Sizable) -> BottomCenterSizable:
        return self.as_bottom_center_of(size)


class BottomRightCoordinate(Coordinate):
    @override
    def as_top_left_of(self, size: Size | Sizable) -> BottomRightSizable:
        return self.as_bottom_right_of(size)
