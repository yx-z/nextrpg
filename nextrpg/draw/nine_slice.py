from dataclasses import dataclass
from functools import cached_property

from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_group import DrawingGroup
from nextrpg.draw.relative_drawing import Anchor, RelativeDrawing
from nextrpg.geometry.coordinate import ORIGIN
from nextrpg.geometry.dimension import (
    ZERO_SIZE,
    Height,
    HeightScaling,
    Pixel,
    Size,
    Width,
    WidthScaling,
)
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen


@dataclass(frozen=True)
class NineSlice:
    drawing: Drawing
    top: Pixel | Height
    left: Pixel | Width
    bottom: Pixel | Height
    right: Pixel | Width

    def stretch(self, size: Size) -> DrawingGroup:
        width_scale = WidthScaling(
            (size.width_value - self._left.value - self._right.value)
            / self._top_center.width.value
        )
        stretched_top_center = self._top_center * width_scale
        stretched_bottom_center = self._bottom_center * width_scale

        height_scale = HeightScaling(
            (size.height_value - self._top.value - self._bottom.value)
            / self._center_left.height.value
        )
        stretched_center_left = self._center_left * height_scale
        stretched_center_right = self._center_right * height_scale
        stretched_center = self._center * width_scale * height_scale

        top_left = RelativeDrawing(self._top_left, ZERO_SIZE)
        top_center = RelativeDrawing(
            stretched_top_center, self._left.with_height(0)
        )
        top_right = RelativeDrawing(
            self._top_right, size.width.with_height(0), Anchor.TOP_RIGHT
        )
        top_row_group = DrawingGroup((top_left, top_center, top_right))
        top_row = RelativeDrawing(top_row_group, ZERO_SIZE)

        center_left = RelativeDrawing(stretched_center_left, ZERO_SIZE)
        center = RelativeDrawing(stretched_center, self._left.with_height(0))
        center_right = RelativeDrawing(
            stretched_center_right,
            size.width.with_height(0),
            Anchor.TOP_RIGHT,
        )
        center_row_group = DrawingGroup((center_left, center, center_right))
        center_row = RelativeDrawing(center_row_group, self._top.with_width(0))

        bottom_left = RelativeDrawing(self._bottom_left, ZERO_SIZE)
        bottom_center = RelativeDrawing(
            stretched_bottom_center, self._left.with_height(0)
        )
        bottom_right = RelativeDrawing(
            self._bottom_right, size.width.with_height(0), Anchor.TOP_RIGHT
        )
        bottom_row_group = DrawingGroup(
            (bottom_left, bottom_center, bottom_right)
        )
        bottom_row = RelativeDrawing(
            bottom_row_group, size.height.with_width(0), Anchor.BOTTOM_LEFT
        )

        return DrawingGroup((top_row, center_row, bottom_row))

    @cached_property
    def _top_left(self) -> Drawing:
        top_left = ORIGIN
        size = Size(self._left.value, self._top.value)
        area = RectangleAreaOnScreen(top_left, size)
        return self.drawing.crop(area)

    @cached_property
    def _top_center(self) -> Drawing:
        top_left = ORIGIN + self._left
        size = Size(self._center_width.value, self._top.value)
        area = RectangleAreaOnScreen(top_left, size)
        return self.drawing.crop(area)

    @cached_property
    def _top_right(self) -> Drawing:
        top_left = ORIGIN + self.drawing.width - self._right
        size = Size(self._right.value, self._top.value)
        area = RectangleAreaOnScreen(top_left, size)
        return self.drawing.crop(area)

    @cached_property
    def _center_left(self) -> Drawing:
        top_left = ORIGIN + self._top
        size = Size(self._left.value, self._center_height.value)
        area = RectangleAreaOnScreen(top_left, size)
        return self.drawing.crop(area)

    @cached_property
    def _center(self) -> Drawing:
        top_left = ORIGIN + self._top + self._left
        size = Size(self._center_width.value, self._center_height.value)
        area = RectangleAreaOnScreen(top_left, size)
        return self.drawing.crop(area)

    @cached_property
    def _center_right(self) -> Drawing:
        top_left = ORIGIN + self.drawing.width - self._right + self._top
        size = Size(self._right.value, self._center_height.value)
        area = RectangleAreaOnScreen(top_left, size)
        return self.drawing.crop(area)

    @cached_property
    def _bottom_left(self) -> Drawing:
        top_left = ORIGIN + self.drawing.height - self._bottom
        size = Size(self._left.value, self._bottom.value)
        area = RectangleAreaOnScreen(top_left, size)
        return self.drawing.crop(area)

    @cached_property
    def _bottom_center(self) -> Drawing:
        top_left = ORIGIN + self._left + self.drawing.height - self._bottom
        size = Size(self._center_width.value, self._bottom.value)
        area = RectangleAreaOnScreen(top_left, size)
        return self.drawing.crop(area)

    @cached_property
    def _bottom_right(self) -> Drawing:
        top_left = ORIGIN + self.drawing.size - self._right - self._bottom
        size = Size(self._right.value, self._bottom.value)
        area = RectangleAreaOnScreen(top_left, size)
        return self.drawing.crop(area)

    @property
    def _top(self) -> Height:
        if isinstance(self.top, Height):
            return self.top
        return Height(self.top)

    @property
    def _left(self) -> Width:
        if isinstance(self.left, Width):
            return self.left
        return Width(self.left)

    @property
    def _bottom(self) -> Height:
        if isinstance(self.bottom, Height):
            return self.bottom
        return Height(self.bottom)

    @property
    def _right(self) -> Width:
        if isinstance(self.right, Width):
            return self.right
        return Width(self.right)

    @property
    def _center_width(self) -> Width:
        return self.drawing.width - self._left - self._right

    @property
    def _center_height(self) -> Height:
        return self.drawing.height - self._top - self._bottom
