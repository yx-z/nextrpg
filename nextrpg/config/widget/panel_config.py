from collections.abc import Callable
from functools import cached_property
from typing import TYPE_CHECKING

from nextrpg.core.dataclass_with_default import dataclass_with_default
from nextrpg.drawing.color import WHITE, Color
from nextrpg.drawing.sprite import Sprite
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.padding import Padding, padding_for_all_sides

if TYPE_CHECKING:
    from nextrpg.drawing.drawing import Drawing


def move_above_icon(
    points: tuple[Coordinate, ...] = (
        Coordinate(10, 0),
        Coordinate(0, 5),
        Coordinate(20, 5),
    ),
    color: Color = WHITE,
) -> Drawing:
    from nextrpg.drawing.polygon_drawing import PolygonDrawing

    return PolygonDrawing(points, color).drawing


@dataclass_with_default(frozen=True)
class PanelConfig:
    padding: Padding = padding_for_all_sides(10)
    more_above_icon_input: Sprite | Callable[[], Sprite] | None = None
    more_below_icon_input: Sprite | Callable[[], Sprite] | None = None
    more_on_left_icon_input: Sprite | Callable[[], Sprite] | None = None
    more_on_right_icon_input: Sprite | Callable[[], Sprite] | None = None

    @cached_property
    def more_above_icon(self) -> Sprite:
        if callable(self.more_above_icon_input):
            return self.more_above_icon_input()
        if self.more_above_icon_input:
            return self.more_above_icon_input
        return move_above_icon()

    @cached_property
    def more_below_icon(self) -> Sprite:
        if callable(self.more_below_icon_input):
            return self.more_below_icon_input()
        if self.more_below_icon_input:
            return self.more_below_icon_input
        return self.more_above_icon.flip(vertical=True)

    @cached_property
    def more_on_left_icon(self) -> Sprite:
        if callable(self.more_on_left_icon_input):
            return self.more_on_left_icon_input()
        if self.more_on_left_icon_input:
            return self.more_on_left_icon_input
        return self.more_above_icon.rotate(90)

    @cached_property
    def more_on_right_icon(self) -> Sprite:
        if callable(self.more_on_right_icon_input):
            return self.more_on_right_icon_input()
        if self.more_on_right_icon_input:
            return self.more_on_right_icon_input
        return self.more_above_icon.rotate(-90)
