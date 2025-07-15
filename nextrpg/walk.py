"""
Path-based walking system for NextRPG.

This module provides a sophisticated walking system that allows characters
and objects to follow predefined paths with configurable movement speeds.
The system supports both linear and cyclic paths, with smooth movement
interpolation between path points.

The walking system includes:
- Path-based movement along polygon paths
- Configurable movement speed
- Support for cyclic (looping) and linear paths
- Smooth interpolation between path points
- Direction calculation based on movement
- Completion detection for linear paths

The system is designed to work seamlessly with the character movement
and animation systems, providing realistic path-following behavior.

Example:
    ```python
    from nextrpg.walk import Walk
    from nextrpg.draw_on_screen import Polygon
    from nextrpg.coordinate import Coordinate

    # Create a path
    path = Polygon([
        Coordinate(0, 0),
        Coordinate(100, 0),
        Coordinate(100, 100),
        Coordinate(0, 100)
    ])

    # Create a walk instance
    walk = Walk(path=path, move_speed=50, cyclic=True)

    # Update movement
    walk = walk.tick(time_delta)
    ```
"""

from dataclasses import replace
from functools import cached_property
from math import hypot
from typing import NamedTuple, Self

from nextrpg.coordinate import Coordinate
from nextrpg.core import Direction, Millisecond, Pixel, PixelPerMillisecond
from nextrpg.draw_on_screen import Polygon
from nextrpg.model import dataclass_with_instance_init, export, instance_init


@export
@dataclass_with_instance_init
class Walk:
    """
    Path-based walking system for characters and objects.

    This class provides a complete walking system that allows entities
    to follow predefined paths with smooth movement. It supports both
    linear paths (with completion) and cyclic paths (looping).

    The walking system calculates movement based on time deltas and
    movement speed, providing smooth interpolation between path points.
    It also tracks direction changes for animation purposes.

    Arguments:
        `path`: The polygon path to follow.

        `move_speed`: Movement speed in pixels per millisecond.

        `cyclic`: Whether the path should loop continuously.
            If `True`, the walk will restart from the beginning
            when reaching the end. If `False`, the walk will
            complete when reaching the end.

        `coordinate`: Current position on the path. Automatically
            initialized to the path's starting point.

        `_last_coordinate`: Previous position for direction calculation.
            Automatically initialized to the path's starting point.

        `_index`: Current path point index.

        `_last_index`: Previous path point index.

    Example:
        ```python
        from nextrpg.walk import Walk
        from nextrpg.draw_on_screen import Polygon
        from nextrpg.coordinate import Coordinate

        # Create a simple rectangular path
        path = Polygon([
            Coordinate(0, 0),
            Coordinate(100, 0),
            Coordinate(100, 100),
            Coordinate(0, 100)
        ])

        # Create a cyclic walk
        walk = Walk(path=path, move_speed=50, cyclic=True)

        # Update in game loop
        walk = walk.tick(time_delta)

        # Check if completed (for non-cyclic paths)
        if walk.completed:
            print("Walk finished!")
        ```
    """

    path: Polygon
    move_speed: PixelPerMillisecond
    cyclic: bool
    coordinate: Coordinate = instance_init(lambda self: self._source)
    _last_coordinate: Coordinate = instance_init(lambda self: self._source)
    _index: int = 0
    _last_index: int = 0

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
        return self.coordinate.relative_to(self._last_coordinate)

    @cached_property
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
        return replace(
            self,
            coordinate=self._source,
            _last_coordinate=self._source,
            _index=0,
            _last_index=0,
        )

    def tick(self, time_delta: Millisecond) -> Self:
        """
        Update the walk state based on elapsed time.

        Advances the walk along the path based on the movement speed
        and elapsed time. For cyclic paths, it will loop back to the
        beginning when reaching the end.

        Arguments:
            `time_delta`: The elapsed time in milliseconds.

        Returns:
            `Walk`: A new walk instance with updated position.

        Example:
            ```python
            # Update walk in game loop
            walk = walk.tick(time_delta)
            ```
        """
        if self.complete:
            return self

        current_coord = self.coordinate
        last_coord = self.coordinate
        index = self._index
        last_index = self._index

        remaining_distance = self.move_speed * time_delta
        if not self.cyclic and remaining_distance > self._remaining_length:
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
        if self.cyclic:
            return False
        if self.path.closed:
            return self._index == 0 and self._last_index != 0
        return self._next_index(self._index) == 0

    def _tick_segment(
        self, current_coord: Coordinate, index: int, max_distance: float
    ) -> _StepResult:
        """
        Update movement along a single path segment.

        Calculates movement within the current path segment, handling
        both complete segment traversal and partial movement.

        Arguments:
            `current_coord`: Current position on the path.

            `index`: Current path point index.

            `max_distance`: Maximum distance to move in this step.

        Returns:
            `_StepResult`: Result of the segment movement.
        """
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
        """
        Check if the given index is the final path point.

        Arguments:
            `index`: The path point index to check.

        Returns:
            `bool`: Whether the index is the final point.
        """
        if self.cyclic:
            return False
        return index >= len(self.path.points) - 1

    def _next_index(self, i: int) -> int:
        """
        Get the next path point index.

        Handles wrapping for cyclic paths by returning 0 when
        reaching the end of the path.

        Arguments:
            `i`: Current path point index.

        Returns:
            `int`: Next path point index.
        """
        stepped = i + 1
        if stepped < len(self.path.points):
            return stepped
        return 0

    @cached_property
    def _source(self) -> Coordinate:
        """
        Get the starting coordinate of the path.

        Returns:
            `Coordinate`: The first point of the path.
        """
        return self.path.points[0]

    @cached_property
    def _remaining_length(self) -> Pixel:
        """
        Calculate the remaining path length from current position.

        Returns:
            `Pixel`: The remaining distance to the end of the path.
        """
        points = self.path.points
        total = 0.0
        start = self.coordinate
        for i in range(self._index, len(points) - 1):
            end = points[i + 1]
            total += hypot(end.left - start.left, end.top - start.top)
            start = end
        return total


class _StepResult(NamedTuple):
    """
    Result of a single step in path movement.

    This named tuple contains the results of moving along a path
    segment, including whether a step was taken, new coordinates,
    and distance information.

    Arguments:
        `stepped`: Whether a complete step to the next point was taken.

        `coordinate`: The new coordinate after movement.

        `last_coordinate`: The previous coordinate before movement.

        `index`: The new path point index.

        `last_index`: The previous path point index.

        `distance_used`: The distance actually moved in this step.
    """

    stepped: bool
    coordinate: Coordinate
    last_coordinate: Coordinate
    index: int
    last_index: int
    distance_used: float
