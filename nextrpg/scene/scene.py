from functools import cached_property
from typing import TYPE_CHECKING

from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.event.base_event import BaseEvent

if TYPE_CHECKING:
    from nextrpg.game.game_state import GameState


class Scene:
    @cached_property
    def drawing_on_screens(self) -> DrawingOnScreens:
        return DrawingOnScreens()

    def tick(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Scene, GameState]:
        return self, state

    def event(
        self, event: BaseEvent, state: GameState
    ) -> tuple[Scene, GameState]:
        return self, state
