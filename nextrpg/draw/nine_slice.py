from dataclasses import dataclass
from functools import cached_property

from nextrpg.core.coordinate import ORIGIN, Coordinate
from nextrpg.core.dimension import HeightScaling, Pixel, Size, WidthScaling
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_group import DrawingGroup
from nextrpg.draw.relative_drawing import RelativeDrawing


@dataclass(frozen=True)
class NineSlice:
    drawing: Drawing
    top: Pixel
    left: Pixel
    bottom: Pixel
    right: Pixel

    def stretch(self, size: Size) -> DrawingGroup:
        width_scale = WidthScaling(
            (size.width.value - self.left - self.right)
            / self._top_center.width.value
        )
        stretched_top_center = self._top_center * width_scale
        stretched_bottom_center = self._bottom_center * width_scale

        height_scale = HeightScaling(
            (size.height_value - self.top - self.bottom)
            / self._center_left.height.value
        )
        stretched_center_left = self._center_left * height_scale
        stretched_center_right = self._center_right * height_scale
        stretched_center = self._center * width_scale * height_scale

        top_left = RelativeDrawing(self._top_left, ORIGIN)
        top_center = RelativeDrawing(stretched_top_center, Size(self.left, 0))
        top_right = RelativeDrawing(
            self._top_right, Size(size.width_value - self.right, 0)
        )
        center_left = RelativeDrawing(stretched_center_left, Size(0, self.top))
        center = RelativeDrawing(stretched_center, Size(self.left, self.top))
        center_right = RelativeDrawing(
            stretched_center_right,
            Size(size.width_value - self.right, self.top),
        )
        bottom_left = RelativeDrawing(
            self._bottom_left, Size(0, size.height_value - self.bottom)
        )
        bottom_center = RelativeDrawing(
            stretched_bottom_center,
            Size(self.left, size.height_value - self.bottom),
        )
        bottom_right = RelativeDrawing(
            self._bottom_right,
            Size(
                size.width_value - self.right,
                size.height_value - self.bottom,
            ),
        )

        relative_drawings = (
            top_left,
            top_center,
            top_right,
            center_left,
            center,
            center_right,
            bottom_left,
            bottom_center,
            bottom_right,
        )
        return DrawingGroup(relative_drawings)

    @cached_property
    def _top_left(self) -> Drawing:
        top_left = ORIGIN
        size = Size(self.left, self.top)
        return self.drawing.crop(top_left, size)

    @cached_property
    def _top_center(self) -> Drawing:
        top_left = Coordinate(self.left, 0)
        size = Size(self.drawing.width.value - self.left - self.right, self.top)
        return self.drawing.crop(top_left, size)

    @cached_property
    def _top_right(self) -> Drawing:
        top_left = Coordinate(self.drawing.width.value - self.right, 0)
        size = Size(self.right, self.top)
        return self.drawing.crop(top_left, size)

    @cached_property
    def _center_left(self) -> Drawing:
        top_left = Coordinate(0, self.top)
        size = Size(
            self.left, self.drawing.height.value - self.top - self.bottom
        )
        return self.drawing.crop(top_left, size)

    @cached_property
    def _center(self) -> Drawing:
        top_left = Coordinate(self.left, self.top)
        size = Size(
            self.drawing.width.value - self.left - self.right,
            self.drawing.height.value - self.top - self.bottom,
        )
        return self.drawing.crop(top_left, size)

    @cached_property
    def _center_right(self) -> Drawing:
        top_left = Coordinate(self.drawing.width.value - self.right, self.top)
        size = Size(
            self.right, self.drawing.height.value - self.top - self.bottom
        )
        return self.drawing.crop(top_left, size)

    @cached_property
    def _bottom_left(self) -> Drawing:
        top_left = Coordinate(0, self.drawing.height.value - self.bottom)
        size = Size(self.left, self.bottom)
        return self.drawing.crop(top_left, size)

    @cached_property
    def _bottom_center(self) -> Drawing:
        top_left = Coordinate(
            self.left, self.drawing.height.value - self.bottom
        )
        size = Size(
            self.drawing.width.value - self.left - self.right, self.bottom
        )
        return self.drawing.crop(top_left, size)

    @cached_property
    def _bottom_right(self) -> Drawing:
        top_left = Coordinate(
            self.drawing.width.value - self.right,
            self.drawing.height.value - self.bottom,
        )
        size = Size(self.right, self.bottom)
        return self.drawing.crop(top_left, size)
