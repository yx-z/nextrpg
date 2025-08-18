from dataclasses import dataclass
from functools import cached_property

from nextrpg.core.coordinate import ORIGIN, Coordinate
from nextrpg.core.dimension import HeightScaling, Pixel, Size, WidthScaling
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_group import DrawingGroup, RelativeDrawing


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
            (size.height.value - self.top - self.bottom)
            / self._center_left.height.value
        )
        stretched_center_left = self._center_left * height_scale
        stretched_center_right = self._center_right * height_scale
        stretched_center = self._center * width_scale * height_scale

        relative_drawings = (
            RelativeDrawing(self._top_left, ORIGIN),
            RelativeDrawing(stretched_top_center, Size(self.left, 0)),
            RelativeDrawing(self._top_right, Size(size.width - self.right, 0)),
            RelativeDrawing(stretched_center_left, Size(0, self.top)),
            RelativeDrawing(stretched_center, Size(self.left, self.top)),
            RelativeDrawing(
                stretched_center_right, Size(size.height - self.right, self.top)
            ),
            RelativeDrawing(
                self._bottom_left, Size(0, size.height - self.bottom)
            ),
            RelativeDrawing(
                stretched_bottom_center,
                Size(self.left, size.height - self.bottom),
            ),
            RelativeDrawing(
                self._bottom_right,
                Size(size.width - self.right, size.height - self.bottom),
            ),
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
        size = Size(self.drawing.width - self.left - self.right, self.top)
        return self.drawing.crop(top_left, size)

    @cached_property
    def _top_right(self) -> Drawing:
        top_left = Coordinate(self.drawing.width - self.right, 0)
        size = Size(self.right, self.top)
        return self.drawing.crop(top_left, size)

    @cached_property
    def _center_left(self) -> Drawing:
        top_left = Coordinate(0, self.top)
        size = Size(self.left, self.drawing.height - self.top - self.bottom)
        return self.drawing.crop(top_left, size)

    @cached_property
    def _center(self) -> Drawing:
        top_left = Coordinate(self.left, self.top)
        size = Size(
            self.drawing.width - self.left - self.right,
            self.drawing.height - self.top - self.bottom,
        )
        return self.drawing.crop(top_left, size)

    @cached_property
    def _center_right(self) -> Drawing:
        top_left = Coordinate(self.drawing.width - self.right, self.top)
        size = Size(self.right, self.drawing.height - self.top - self.bottom)
        return self.drawing.crop(top_left, size)

    @cached_property
    def _bottom_left(self) -> Drawing:
        top_left = Coordinate(0, self.drawing.height - self.bottom)
        size = Size(self.left, self.bottom)
        return self.drawing.crop(top_left, size)

    @cached_property
    def _bottom_center(self) -> Drawing:
        top_left = Coordinate(self.left, self.drawing.height - self.bottom)
        size = Size(self.drawing.width - self.left - self.right, self.bottom)
        return self.drawing.crop(top_left, size)

    @cached_property
    def _bottom_right(self) -> Drawing:
        top_left = Coordinate(
            self.drawing.width - self.right, self.drawing.height - self.bottom
        )
        size = Size(self.right, self.bottom)
        return self.drawing.crop(top_left, size)
