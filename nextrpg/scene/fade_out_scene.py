from dataclasses import KW_ONLY, field, replace
from functools import cached_property

from nextrpg.animation.fade import FadeOut
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.scene.scene import Scene


@dataclass_with_default(frozen=True)
class FadeOutScene(Scene):
    from_scene: Scene
    to_scene: Scene
    duration: Millisecond = field(
        default_factory=lambda: config().timing.fade_duration
    )
    _: KW_ONLY = private_init_below()
    _fade_out: FadeOut = default(
        lambda self: FadeOut(self.from_scene, self.duration)
    )

    def tick(self, time_delta: Millisecond) -> Scene:
        to_scene = self.to_scene.tick(time_delta)
        if (fade_out := self._fade_out.tick(time_delta)).is_complete:
            return to_scene
        from_scene = self.from_scene.tick(time_delta)
        return replace(
            self, from_scene=from_scene, to_scene=to_scene, _fade_out=fade_out
        )

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return (
            self.to_scene.drawing_on_screens + self._fade_out.drawing_on_screens
        )
