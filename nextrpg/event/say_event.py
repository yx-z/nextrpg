from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npcs import RpgEventScene
from nextrpg.config.say_event_config import SayEventConfig
from nextrpg.config.config import config
from nextrpg.draw.coordinate import Coordinate
from nextrpg.core import Millisecond, Size
from nextrpg.draw.draw_on_screen import DrawOnScreen, Drawing, Rectangle
from nextrpg.draw.fade_in import FadeIn
from nextrpg.draw.fade_out import FadeOut
from nextrpg.draw.text import Text
from nextrpg.event.pygame_event import KeyPressDown, KeyboardKey, PygameEvent
from nextrpg.gui.area import screen
from nextrpg.model import dataclass_with_instance_init, instance_init
from nextrpg.scene.scene import Scene
from nextrpg.draw.text_on_screen import TextOnScreen


@dataclass_with_instance_init
class SayEvent(RpgEventScene):
    """
    `say` scene.

    Arguments:
        `message`: The message to say.
    """

    character_or_scene: CharacterOnScreen | Scene
    message: str
    arg: Coordinate | Drawing | None = None
    config: SayEventConfig = field(default_factory=lambda: config().say_event)
    _background_fade_in: FadeIn = instance_init(
        lambda self: FadeIn(
            resource=self._pop_up,
            duration=self.config.fade_duration,
        )
    )
    _fade_out: bool = False
    _pop_up_fade_out: FadeOut = instance_init(
        lambda self: FadeOut(
            resource=self._pop_up + self._text_on_screen,
            duration=self.config.fade_duration,
        )
    )

    @cached_property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        if self._fade_out:
            return (
                self.scene.draw_on_screens
                + self._pop_up_fade_out.draw_on_screens
            )
        return (
            self.scene.draw_on_screens
            + self._background_fade_in.draw_on_screens
            + self._text_on_screen
        )

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if self._pop_up_fade_out.complete:
            return self.scene.send(self.generator)
        scene = self.scene.tick_without_event(time_delta)
        if self._fade_out:
            return replace(
                self,
                scene=scene,
                _pop_up_fade_out=self._pop_up_fade_out.tick(time_delta),
            )
        return replace(
            self,
            scene=scene,
            _background_fade_in=self._background_fade_in.tick(time_delta),
        )

    @override
    def event(self, e: PygameEvent) -> Scene:
        if not isinstance(e, KeyPressDown):
            scene = self.scene.event_without_npc_trigger(e)
            return replace(self, scene=scene)

        if e.key is KeyboardKey.CONFIRM:
            return replace(self, _fade_out=True)
        return self

    @cached_property
    def _text_on_screen(self) -> tuple[DrawOnScreen, ...]:
        if self._background_fade_in.complete:
            return TextOnScreen(self._text_top_left, self._text).draw_on_screens
        return ()

    @cached_property
    def _pop_up(self) -> tuple[DrawOnScreen, ...]:
        return (self._background,) + self._text_tail

    @cached_property
    def _text_tail(self) -> tuple[DrawOnScreen, ...]:
        return ()

    @cached_property
    def _text(self) -> Text:
        return Text(self.message, self.config.text)

    @cached_property
    def _text_top_left(self) -> Coordinate:
        if isinstance(self.character_or_scene, Scene):
            return self._scene_top_left

        coord = self.character_or_scene.coordinate
        if self.scene.draw_on_screen_shift:
            return coord.shift(self.scene.draw_on_screen_shift)
        return coord

    @cached_property
    def _scene_top_left(self) -> Coordinate:
        center = (
            self.arg if isinstance(self.arg, Coordinate) else screen().center
        )
        width, height = self._text.size
        return center.shift(Coordinate(width / 2, height / 2).negate)

    @cached_property
    def _background(self) -> DrawOnScreen:
        width, height = self._text.size
        top_left = self._text_top_left.shift(
            Coordinate(self.config.padding, self.config.padding).negate
        )
        padding = self.config.padding * 2
        size = Size(width + padding, height + padding)
        return Rectangle(top_left, size).fill(
            self.config.background, self.config.border_radius
        )
