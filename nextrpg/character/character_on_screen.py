"""
Handles character movement and collision detection.
"""

from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.core import Millisecond
from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.draw.coordinate import Coordinate
from nextrpg.event.rpg_event import registered_events
from nextrpg.model import (
    NEXTRPG_INSTANCE_INIT,
    dataclass_with_instance_init,
    instance_init,
)
from nextrpg.scene.scene import Scene

type CharacterVisual = Callable[[CharacterOnScreen], tuple[DrawOnScreen, ...]]


@dataclass_with_instance_init
class CharacterSpec:
    name: str
    display_name: str = instance_init(lambda self: self.name)
    character: CharacterDrawing
    below_foreground_visuals: tuple[CharacterVisual, ...] = ()
    above_foreground_visuals: tuple[CharacterVisual, ...] = ()


@dataclass_with_instance_init
class CharacterOnScreen:
    """
    Represents a character that can be displayed and moved on screen.

    Handles character movement, collision detection, and event processing for
    character interactions with the game environment.

    Arguments:
        `character_drawing`: The visual representation of the character.

        `coordinate`: The current position of the character on screen.

        `speed`: Movement speed of the character in pixels.

        `collisions`: Tuple of polygons representing collision boundaries.
    """

    spec: CharacterSpec
    coordinate: Coordinate
    name: str = instance_init(lambda self: self.spec.display_name)
    character: CharacterDrawing = instance_init(
        lambda self: self.spec.character
    )
    _event_triggered: bool = False

    @cached_property
    def character_and_visuals(self) -> tuple[DrawOnScreen, ...]:
        below = self._visuals(self.spec.below_foreground_visuals)
        above = self._visuals(self.spec.above_foreground_visuals)
        return below + (self.draw_on_screen,) + above

    @cached_property
    def draw_on_screen(self) -> DrawOnScreen:
        """
        Creates drawable representations of the character and visuals.

        Returns:
            `CharacterAndVisuals`: A tuple containing the character's drawable
            representation and any associated visual elements.
        """
        return DrawOnScreen(self.coordinate, self.character.drawing)

    def tick(self, time_delta: Millisecond) -> Self:
        """
        Update the character's state for a single game loop.

        Arguments:
            `time_delta`: The elapsed time since the last update.

        Returns:
            `CharacterOnScreen`: The updated character state after the step.
        """
        return replace(self, character=self.character.tick_idle(time_delta))

    def start_event(self, character: CharacterOnScreen) -> Self:
        direction = character.coordinate.relative_to(self.coordinate)
        turned_character = self.character.turn(direction)
        return replace(self, character=turned_character, _event_triggered=True)

    @cached_property
    def complete_event(self) -> Self:
        return replace(self, _event_triggered=False)

    def __getattr__(self, attr: str) -> Callable[..., Scene] | None:
        if event := registered_events.get(attr):
            return lambda *args, **kwargs: event(self, *args, **kwargs)
        if attr == NEXTRPG_INSTANCE_INIT:
            return None
        raise AttributeError(
            f"{attr} is neither a registered RPG event nor a member of {self}."
        )

    def _visuals(
        self, visuals: tuple[CharacterVisual, ...]
    ) -> tuple[DrawOnScreen, ...]:
        return tuple(d for f in visuals for d in f(self))
