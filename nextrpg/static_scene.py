from dataclasses import dataclass, field
from functools import cached_property

from nextrpg.global_config import config
from nextrpg.core import Rgba
from nextrpg.draw_on_screen import DrawOnScreen
from nextrpg.area import screen
from nextrpg.transition_scene import TransitioningScene
from nextrpg.model import export


@export
@dataclass(frozen=True)
class StaticScene(TransitioningScene):
    resource: Rgba | DrawOnScreen = field(
        default_factory=lambda: config().gui.background_color
    )

    @cached_property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        if isinstance(self.resource, Rgba):
            return (screen().fill(self.resource),)
        return (self.resource,)
