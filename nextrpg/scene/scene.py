from functools import cached_property
from typing import TYPE_CHECKING

from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent

if TYPE_CHECKING:
    from nextrpg.game.game_state import GameState


class Scene:
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return ()

    def tick(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Scene, GameState]:
        return self, state

    def event(
        self, event: IoEvent, state: GameState
    ) -> tuple[Scene, GameState]:
        return self, state
