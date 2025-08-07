from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Height, Size, Width


class Sizeable:
    top_left: Coordinate
    size: Size

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
        return self.top_left + self.height / 2

    @property
    def center_left(self) -> Coordinate:
        return self.top_left + self.height / 2

    @property
    def center_right(self) -> Coordinate:
        return self.top_right + self.height / 2

    @property
    def center(self) -> Coordinate:
        return self.top_center + self.height / 2
