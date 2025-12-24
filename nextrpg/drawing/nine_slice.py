from dataclasses import dataclass
from functools import cached_property

from nextrpg.config.config import config
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.polyline_drawing import PolylineDrawing
from nextrpg.drawing.sprite import Sprite
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import ORIGIN
from nextrpg.geometry.size import Height, Size, Width


@dataclass(frozen=True)
class NineSlice:
    sprite: Sprite
    top: Height
    left: Width
    bottom: Height
    right: Width

    def stretch(self, size: Size) -> DrawingGroup:
        width_scale = (
            size.width - self.left - self.right
        ) / self._top_center.width
        height_scale = (
            size.height - self.top - self.bottom
        ) / self._center_left.height

        stretched_top_center = self._top_center * width_scale
        top_row = self._stretch_row(
            size, self._top_left, stretched_top_center, self._top_right
        )

        stretched_center_left = self._center_left * height_scale
        stretched_center = self._center * width_scale * height_scale
        stretched_center_right = self._center_right * height_scale
        center_row_group = self._stretch_row(
            size,
            stretched_center_left,
            stretched_center,
            stretched_center_right,
        )
        center_row = center_row_group + self.top.size

        stretched_bottom_center = self._bottom_center * width_scale
        bottom_row_group = self._stretch_row(
            size, self._bottom_left, stretched_bottom_center, self._bottom_right
        )
        bottom_row = bottom_row_group.shift(size.height, Anchor.BOTTOM_LEFT)

        parts = [top_row, center_row, bottom_row]
        if (debug := config().debug) and (color := debug.drawing_group_link):
            points = (ORIGIN, size.height.size.coordinate)
            vertical_line = PolylineDrawing(points, color).drawing
            parts += [
                vertical_line + self.left.size,
                vertical_line + (size.width - self.right).size,
            ]
        return DrawingGroup(tuple(parts))

    def _stretch_row(
        self, size: Size, left: Sprite, center: Sprite, right: Sprite
    ) -> DrawingGroup:
        relative_center = center + self.left.size
        relative_right = right.shift(size.width, Anchor.TOP_RIGHT)
        return DrawingGroup((left, relative_center, relative_right))

    @cached_property
    def _top_left(self) -> Sprite:
        size = self.left * self.top
        area = ORIGIN.as_top_left_of(size).rectangle_area_on_screen
        return self.sprite.crop(area)

    @cached_property
    def _top_center(self) -> Sprite:
        top_left = ORIGIN + self.left
        size = self._center_width * self.top
        area = top_left.as_top_left_of(size).rectangle_area_on_screen
        return self.sprite.crop(area)

    @cached_property
    def _top_right(self) -> Sprite:
        top_left = ORIGIN + self.sprite.width - self.right
        size = self.right * self.top
        area = top_left.as_top_left_of(size).rectangle_area_on_screen
        return self.sprite.crop(area)

    @cached_property
    def _center_left(self) -> Sprite:
        top_left = ORIGIN + self.top
        size = self.left * self._center_height
        area = top_left.as_top_left_of(size).rectangle_area_on_screen
        return self.sprite.crop(area)

    @cached_property
    def _center(self) -> Sprite:
        top_left = ORIGIN + self.top + self.left
        size = self._center_width * self._center_height
        area = top_left.as_top_left_of(size).rectangle_area_on_screen
        return self.sprite.crop(area)

    @cached_property
    def _center_right(self) -> Sprite:
        top_left = ORIGIN + self.sprite.width - self.right + self.top
        size = self.right * self._center_height
        area = top_left.as_top_left_of(size).rectangle_area_on_screen
        return self.sprite.crop(area)

    @cached_property
    def _bottom_left(self) -> Sprite:
        top_left = ORIGIN + self.sprite.height - self.bottom
        size = self.left * self.bottom
        area = top_left.as_top_left_of(size).rectangle_area_on_screen
        return self.sprite.crop(area)

    @cached_property
    def _bottom_center(self) -> Sprite:
        top_left = ORIGIN + self.left + self.sprite.height - self.bottom
        size = self._center_width * self.bottom
        area = top_left.as_top_left_of(size).rectangle_area_on_screen
        return self.sprite.crop(area)

    @cached_property
    def _bottom_right(self) -> Sprite:
        top_left = ORIGIN + self.sprite.size - self.right - self.bottom
        size = self.right * self.bottom
        area = top_left.anchor(size).rectangle_area_on_screen
        return self.sprite.crop(area)

    @cached_property
    def _center_width(self) -> Width:
        return self.sprite.width - self.left - self.right

    @cached_property
    def _center_height(self) -> Height:
        return self.sprite.height - self.top - self.bottom
