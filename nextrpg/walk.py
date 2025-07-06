from dataclasses import dataclass, replace
from functools import cached_property
from math import hypot
from typing import Self

from nextrpg.core import Direction, Millisecond, PixelPerMillisecond
from nextrpg.draw_on_screen import Polygon
from nextrpg.coordinate import Coordinate
from nextrpg.model import instance_init, register_instance_init


@register_instance_init
class Walk:
    path: Polygon
    move_speed: PixelPerMillisecond
    cyclic: bool
    coordinate: Coordinate = instance_init(lambda self: self.path.points[0])
    _last_coordinate: Coordinate = instance_init(lambda self: self.coordinate)
    _index: int = 0
    _last_index: int = 0

    @cached_property
    def direction(self) -> Direction:
        return self.coordinate.direction(self._last_coordinate)

    @cached_property
    def reset(self) -> Self:
        return Walk(path=self.path, move_speed=self.move_speed)

    @cached_property
    def is_completed(self) -> bool:
        if self.cyclic:
            return False

        return (
            self._index == 0 and self._last_index != 0
            if self.path.is_closed
            else self._next_index == 0
        )

    def tick(self, time_delta: Millisecond) -> Self:
        if self.is_completed:
            return self

        end = self.path.points[self._next_index]
        dx = end.left - self.coordinate.left
        dy = end.top - self.coordinate.top

        distance = hypot(dx, dy)
        max_distance = self.move_speed * time_delta
        if distance <= max_distance:
            return replace(
                self,
                coordinate=end,
                _last_coordinate=self.coordinate,
                _index=self._next_index,
                _last_index=self._index,
            )

        ratio = max_distance / distance
        new_x = self.coordinate.left + dx * ratio
        new_y = self.coordinate.top + dy * ratio
        return replace(
            self,
            coordinate=Coordinate(new_x, new_y),
            _last_coordinate=self.coordinate,
        )

    @cached_property
    def _next_index(self) -> int:
        return nex if (nex := self._index + 1) < len(self.path.points) else 0
