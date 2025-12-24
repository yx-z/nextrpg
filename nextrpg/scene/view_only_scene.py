from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.config.config import config
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.drawing.sprite_on_screen import SpriteOnScreen
from nextrpg.game.game_state import GameState
from nextrpg.gui.screen_area import screen_area
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class ViewOnlyScene(Scene):
    resource: SpriteOnScreen = field(
        default_factory=lambda: screen_area().fill(
            config().system.window.background
        )
    )

    @override
    @cached_property
    def drawing_on_screens(self) -> DrawingOnScreens:
        return self.resource.drawing_on_screens

    @override
    def tick(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Self, GameState]:
        resource = self.resource.tick(time_delta)
        ticked = replace(self, resource=resource)
        return ticked, state
