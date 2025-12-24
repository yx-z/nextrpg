from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.fade import FadeOut
from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.character.character_on_screen import CharacterOnScreen
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
    EventGenerator,
    EventScene,
    register_rpg_event_scene,
)
from nextrpg.event.event_transformer import register_rpg_event
from nextrpg.event.eventful_scene import EventfulScene
from nextrpg.event.update_from_event import update_from_event
from nextrpg.game.game_state import GameState
from nextrpg.scene.scene import Scene


@dataclass(frozen=True, kw_only=True)
class BackgroundFadeOutEvent(BackgroundEvent):
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
        return self.fade.is_complete


@dataclass_with_default(frozen=True)
class FadeOutEventScene(EventScene):
    resource: BackgroundEventSentinel | SpriteOnScreen
    wait: bool = True
    duration: Millisecond = field(
        default_factory=lambda: config().animation.default_timed_animation_duration
    )
    _: KW_ONLY = private_init_below()
    _fade: TimedAnimationOnScreens = default(lambda self: self._init_fade)

    @override
    @cached_property
    def drawing_on_screens_after_parent(self) -> DrawingOnScreens:
        return self._fade.drawing_on_screens

    @override
    def _tick_after_parent(
        self, time_delta: Millisecond, ticked: Self, state: GameState
    ) -> tuple[Scene, GameState]:
        if self._is_sentinel_based:
            scene = ticked.parent.remove_background_event(self.resource)
        else:
            scene = ticked.parent

        fade = self._fade.tick(time_delta)
        if not self.wait:
            background_event = BackgroundFadeOutEvent(fade=fade)
            ticked = scene.complete(background_event=background_event)
        elif fade.is_complete:
            ticked = scene.complete()
        else:
            ticked = replace(ticked, parent=scene, _fade=fade)
        return ticked, state

    @cached_property
    def _is_sentinel_based(self) -> bool:
        return isinstance(self.resource, BackgroundEventSentinel)

    @property
    def _init_fade(self) -> TimedAnimationOnScreens:
        if self._is_sentinel_based:
            resource = self.parent.get_background_event(
                self.resource
            ).drawing_on_screens
        else:
            resource = self.resource
        return animate_on_screen(resource, FadeOut, duration=self.duration)


@register_rpg_event_scene(FadeOutEventScene)
def fade_out(
    sentinel: BackgroundEventSentinel | SpriteOnScreen,
    wait: bool = True,
    duration: Millisecond | None = None,
) -> None: ...


@register_rpg_event
def fade_out_character(
    scene: EventfulScene, character: CharacterOnScreen
) -> EventGenerator:
    drawing_on_screen = scene.drawing_on_screens_after_shift(
        character.drawing_on_screens
    )
    yield fade_out(drawing_on_screen, wait=False)
    yield update_from_event(character.transparent_drawing)
