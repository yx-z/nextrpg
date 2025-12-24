from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.fade import FadeIn
from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.drawing.sprite_on_screen import (
    SpriteOnScreen,
    animate_on_screen,
)
from nextrpg.event.background_event import (
    BackgroundEvent,
    BackgroundEventSentinel,
)
from nextrpg.event.event_scene import (
    EventScene,
    register_rpg_event_scene,
)
from nextrpg.event.eventful_scene import EventfulScene
from nextrpg.game.game_state import GameState
from nextrpg.scene.scene import Scene


@dataclass(frozen=True, kw_only=True)
class BackgroundFadeInEvent(BackgroundEvent):
    fade: TimedAnimationOnScreens

    @override
    @cached_property
    def drawing_on_screens(self) -> DrawingOnScreens:
        return self.fade.drawing_on_screens

    @override
    def tick_with_state(
        self, time_delta: Millisecond, scene: EventfulScene, state: GameState
    ) -> tuple[Self, EventfulScene, GameState]:
        fade = self.fade.tick(time_delta)
        ticked = replace(self, fade=fade)
        return ticked, scene, state

    @override
    @cached_property
    def is_complete(self) -> bool:
        return False


@dataclass_with_default(frozen=True)
class FadeInEventScene(EventScene):
    resource: SpriteOnScreen
    wait: bool = True
    duration: Millisecond = field(
        default_factory=lambda: config().animation.default_timed_animation_duration
    )
    _: KW_ONLY = private_init_below()
    _fade: TimedAnimationOnScreens = default(
        lambda self: animate_on_screen(
            self.resource, FadeIn, duration=self.duration
        )
    )

    @override
    @cached_property
    def drawing_on_screens_after_parent(self) -> DrawingOnScreens:
        return self._fade.drawing_on_screens

    @override
    def _tick_after_parent(
        self, time_delta: Millisecond, ticked: Self, state: GameState
    ) -> tuple[Scene, GameState]:
        fade = self._fade.tick(time_delta)
        if self.wait and not fade.is_complete:
            ticked = replace(ticked, _fade=fade)
        else:
            background_fade_in = BackgroundFadeInEvent(fade=fade)
            ticked = ticked.parent.complete(
                background_fade_in.sentinel, background_fade_in
            )
        return ticked, state


@register_rpg_event_scene(FadeInEventScene)
def fade_in(
    resource: SpriteOnScreen,
    wait: bool = True,
    duration: Millisecond | None = None,
) -> BackgroundEventSentinel: ...
