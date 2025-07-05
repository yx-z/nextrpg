"""
EventfulScene interface.
"""

from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self

from nextrpg.character.npcs import RpgEventGenerator
from nextrpg.scene.scene import Scene


@dataclass
class EventfulScene[T](Scene):
    """
    EventfulScene allows scenes to continue event execution via coroutine/
        generator.
    """

    _event: RpgEventGenerator[T] | None = None
    _event_result: T | None = None

    @cached_property
    def next_event(self) -> Scene | None:
        """
        Get the scene for next event.

        Returns:
            `Scene | None`: The next scene to continue event execution, if any.
        """
        if not self._event:
            return None
        try:
            return self._event.send(self._event_result)(self._event, self)
        except StopIteration:
            return self.event_complete

    @cached_property
    def event_complete(self) -> Self:
        """
        Get the scene upon event execution completion.

        Returns:
            `Scene`: The scene upon event execution completion.
        """
        return replace(self, _event=None, _event_result=None)

    def send(self, event: RpgEventGenerator, result: T | None = None) -> Self:
        """
        Continue event execution and optionally send the result of
        the current event.

        Arguments:
            `event`: The generator to generate the next event.

            `result`: Result of the current event, passing to the generator.

        Returns:
            `Scene`: The scene that shall continue with the next event.
        """
        return replace(self, _event=event, _event_result=result)
