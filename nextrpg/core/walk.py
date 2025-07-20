"""
Path-based walking system for `NextRPG`.

This module provides a sophisticated walking system that allows characters and
objects to follow predefined paths with configurable movement speeds. The system
supports both linear and cyclic paths, with smooth movement interpolation
between path points.

The walking system includes:
- Path-based movement along polygon paths
- Configurable movement speed
- Support for cyclic (looping) and linear paths
- Smooth interpolation between path points
- Direction calculation based on movement
- Completion detection for linear paths

The system is designed to work seamlessly with the character movement and
animation systems, providing realistic path-following behavior.
"""

from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import Self

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Pixel, PixelPerMillisecond
from nextrpg.core.direction import Direction
from nextrpg.core.model import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw_on_screen import Polygon


@dataclass_with_instance_init
class Walk:
    """
    Path-based walking system for characters and objects.

    This class provides a complete walking system that allows entities to follow
    predefined paths with smooth movement. It supports both linear paths (with
    completion) and cyclic paths (looping).

    The walking system calculates movement based on time deltas and movement
    speed, providing smooth interpolation between path points. It also tracks
    direction changes for animation purposes.

    Arguments:
        `path`: The polygon path to follow.
        `move_speed`: Movement speed in pixels per millisecond.
        `cyclic`: Whether the path should loop continuously. If `True`, the walk
            will restart from the beginning when reaching the end. If `False`,
            the walk will complete when reaching the end.
        `coordinate`: Current position on the path. Automatically initialized to
            the path's starting point.
        `_last_coordinate`: Previous position for direction calculation.
            Automatically initialized to the path's starting point.
        `_index`: Current path point index.
        `_last_index`: Previous path point index.
    """

    path: Polygon
    move_speed: PixelPerMillisecond
    cyclic: bool
    _: KW_ONLY = not_constructor_below()
    coordinate: Coordinate = instance_init(lambda self: self.path.points[0])
    _target_index: int | None = 1

    @cached_property
    def direction(self) -> Direction:
        """
        Get the current movement direction.

        Calculates the direction based on the current position
        relative to the previous position.

        Returns:
            `Direction`: The current movement direction.

        Example:
            ```python
            direction = walk.direction
            if direction == Direction.UP:
                # Character is moving upward
                pass
            ```
        """
        if self._target_index is None:
            if self.path.closed:
                last = self.path.points[0]
                penultimate = self.path.points[-1]
            else:
                last = self.path.points[-1]
                penultimate = self.path.points[-2]
            return last.relative_to(penultimate)

        target = self.path.points[self._target_index]
        current = self.path.points[self._target_index - 1]
        return target.relative_to(current)

    @property
    def reset(self) -> Self:
        """
        Reset the walk to its starting position.

        Returns a new walk instance with all internal state
        reset to the beginning of the path.

        Returns:
            `Walk`: A new walk instance reset to the start.

        Example:
            ```python
            # Reset walk to beginning
            walk = walk.reset
            ```
        """
        return replace(self, coordinate=self.path.points[0], _target_index=1)

    def tick(self, time_delta: Millisecond) -> Self:
        """
        Update the walk state based on elapsed time.

        Optimized to:
        - Immediately jump to the final position if a non-cyclic walk exceeds total distance.
        - Use modulo on distance if a cyclic walk exceeds one full path length.

        Arguments:
            `time_delta`: The elapsed time in milliseconds.

        Returns:
            `Walk`: A new walk instance with updated position.
        """
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
                coordinate = Coordinate(x, y)
                break

            remaining_dist -= dist_to_target
            coordinate = target
            index = self._next_index(index)

        return replace(self, coordinate=coordinate, _target_index=index)

    @property
    def complete(self) -> bool:
        """
        Check if the walk has completed.

        For linear paths, returns `True` when the walk has reached
        the end of the path. For cyclic paths, always returns `False`
        since they loop indefinitely.

        Returns:
            `bool`: Whether the walk has completed.

        Example:
            ```python
            if walk.completed:
                print("Walk finished!")
                # Handle completion logic
            ```
        """
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
    def _final_target(self) -> Coordinate:
        if self.path.closed:
            return self.path.points[0]
        return self.path.points[-1]
