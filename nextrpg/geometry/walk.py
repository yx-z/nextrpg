from __future__ import annotations

from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import Self

from nextrpg.core.dataclass_with_default_init import (
    dataclass_with_default_init,
    default_init,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Pixel, PixelPerMillisecond
from nextrpg.geometry.direction import Direction
from nextrpg.geometry.polyline_on_screen import PolylineOnScreen


@dataclass_with_default_init(frozen=True)
class Walk:
    path: PolylineOnScreen
    move_speed: PixelPerMillisecond
    cyclic: bool
    _: KW_ONLY = not_constructor_below()
    coordinate: Coordinate = default_init(lambda self: self._initial_point)
    _target_index: int | None = 1

    @cached_property
    def direction(self) -> Direction:
        if self._target_index is None:
            penultimate = self.path.points[-2]
            return self._final_target.relative_to(penultimate)

        target = self.path.points[self._target_index]
        current = self.path.points[self._target_index - 1]
        return target.relative_to(current)

    @property
    def reset(self) -> Self:
        return replace(self, coordinate=self._initial_point, _target_index=1)

    def tick(self, time_delta: Millisecond) -> Self:
        if self.complete:
            return self

        total_dist = self.move_speed * time_delta
        if not self.cyclic and total_dist >= self._remaining_dist:
            return replace(
                self, coordinate=self._final_target, _target_index=None
            )

        remaining_dist = total_dist % self.path.length
        coordinate = self.coordinate
        index = self._target_index

        while remaining_dist:
            target = self.path.points[index]
            dist_to_target = coordinate.distance(target)
            if remaining_dist < dist_to_target:
                factor = remaining_dist / dist_to_target
                x = coordinate.left + (target.left - coordinate.left) * factor
                y = coordinate.top + (target.top - coordinate.top) * factor
                coordinate = Coordinate(x.value, y.value)
                break

            remaining_dist -= dist_to_target
            coordinate = target
            index = self._next_index(index)

        return replace(self, coordinate=coordinate, _target_index=index)

    @property
    def complete(self) -> bool:
        return self._target_index is None

    def _next_index(self, index: int) -> int:
        stepped = index + 1
        if stepped == len(self.path.points):
            return 0
        return stepped

    @cached_property
    def _remaining_dist(self) -> Pixel:
        points = self.path.points
        reaming_poly = replace(self.path, points=points[self._target_index :])
        return (
            points[self._target_index].distance(self.coordinate)
            + reaming_poly.length
        )

    @property
    def _initial_point(self) -> Coordinate:
        return self.path.points[0]

    @property
    def _final_target(self) -> Coordinate:
        return self.path.points[-1]
