from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import override

from nextrpg.config.config import config
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_on_screen_like import AnimationOnScreenLike
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.gui.screen_area import screen_area
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class ViewOnlyScene(Scene):
    resource: AnimationOnScreenLike = field(
        default_factory=lambda: screen_area().fill(config().window.background)
    )

    @override
    @cached_property
    def drawing_on_screens(self) -> list[DrawingOnScreen]:
        return self.resource.drawing_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        resource = self.resource.tick(time_delta)
        return replace(self, resource=resource)
