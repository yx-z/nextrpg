from dataclasses import replace
from functools import cached_property
from math import hypot
from typing import NamedTuple, Self

from nextrpg.coordinate import Coordinate
from nextrpg.core import Direction, Millisecond, Pixel, PixelPerMillisecond
from nextrpg.draw_on_screen import Polygon
from nextrpg.model import dataclass_with_instance_init, instance_init


@dataclass_with_instance_init
class Walk:
    path: Polygon
    move_speed: PixelPerMillisecond
    cyclic: bool
    coordinate: Coordinate = instance_init(lambda self: self._source)
    _last_coordinate: Coordinate = instance_init(lambda self: self._source)
    _index: int = 0
    _last_index: int = 0

    @cached_property
    def direction(self) -> Direction:
        return self.coordinate.relative_to(self._last_coordinate)

    @cached_property
    def reset(self) -> Self:
        return replace(
            self,
            coordinate=self._source,
            _last_coordinate=self._source,
            _index=0,
            _last_index=0,
        )

    def tick(self, time_delta: Millisecond) -> Self:
        if self.completed:
            return self

        current_coord = self.coordinate
        last_coord = self.coordinate
        index = self._index
        last_index = self._index

        remaining_distance = self.move_speed * time_delta
        if self.cyclic:
            remaining_distance %= self.path.length
        else:
            if remaining_distance > self._remaining_length:
                return replace(
                    self,
                    coordinate=self.path.points[-1],
                    _last_coordinate=current_coord,
                    _index=len(self.path.points) - 1,
                    _last_index=index,
                )

        while remaining_distance > 0 and not self._is_final_index(index):
            step = self._tick_segment(current_coord, index, remaining_distance)
            remaining_distance -= step.distance_used
            current_coord = step.coordinate
            last_coord = step.last_coordinate
            index = step.index
            last_index = step.last_index
            if not step.stepped:
                break

        return replace(
            self,
            coordinate=current_coord,
            _last_coordinate=last_coord,
            _index=index,
            _last_index=last_index,
        )

    @cached_property
    def completed(self) -> bool:
        if self.cyclic:
            return False
        if self.path.closed:
            return self._index == 0 and self._last_index != 0
        return self._next_index(self._index) == 0

    def _tick_segment(
        self, current_coord: Coordinate, index: int, max_distance: float
    ) -> _StepResult:
        next_index = self._next_index(index)
        end = self.path.points[next_index]
        dx = end.left - current_coord.left
        dy = end.top - current_coord.top
        segment_distance = hypot(dx, dy)

        if segment_distance <= max_distance:
            return _StepResult(
                stepped=True,
                coordinate=end,
                last_coordinate=current_coord,
                index=next_index,
                last_index=index,
                distance_used=segment_distance,
            )

        ratio = max_distance / segment_distance
        new_x = current_coord.left + dx * ratio
        new_y = current_coord.top + dy * ratio
        return _StepResult(
            stepped=False,
            coordinate=Coordinate(new_x, new_y),
            last_coordinate=current_coord,
            index=index,
            last_index=index,
            distance_used=max_distance,
        )

    def _is_final_index(self, index: int) -> bool:
        if self.cyclic:
            return False
        return index >= len(self.path.points) - 1

    def _next_index(self, i: int) -> int:
        return i + 1 if i + 1 < len(self.path.points) else 0

    @cached_property
    def _source(self) -> Coordinate:
        return self.path.points[0]

    @cached_property
    def _remaining_length(self) -> Pixel:
        points = self.path.points
        total = 0.0
        start = self.coordinate
        for i in range(self._index, len(points) - 1):
            end = points[i + 1]
            total += hypot(end.left - start.left, end.top - start.top)
            start = end
        return total


class _StepResult(NamedTuple):
    stepped: bool
    coordinate: Coordinate
    last_coordinate: Coordinate
    index: int
    last_index: int
    distance_used: float
