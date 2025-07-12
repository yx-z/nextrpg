from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npcs import RpgEventScene
from nextrpg.config import SayEventConfig, config
from nextrpg.draw.coordinate import Coordinate
from nextrpg.core import Millisecond
from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.event.pygame_event import KeyPressDown, KeyboardKey, PygameEvent
from nextrpg.logger import Logger
from nextrpg.scene.scene import Scene
from nextrpg.draw.text import Text


@dataclass(frozen=True)
class SayEvent(RpgEventScene):
    """
    `say` scene.

    Arguments:
        `message`: The message to say.
    """

    character_or_scene: CharacterOnScreen | Scene
    message: str
    config: SayEventConfig = field(default_factory=lambda: config().say_event)

    @cached_property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        text = Text(
            self.message, self._coordinate, config=self.config.text
        ).draw_on_screen
        return self.scene.draw_on_screens + (text,)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        return replace(self, scene=self.scene.tick_without_event(time_delta))

    @override
    def event(self, e: PygameEvent) -> Scene:
        if not isinstance(e, KeyPressDown):
            scene = self.scene.event_without_npc_trigger(e)
            return replace(self, scene=scene)

        if e.key is KeyboardKey.CONFIRM:
            return self.scene.send(self.generator)
        return self

    @cached_property
    def _coordinate(self) -> Coordinate:
        coord = self.character_or_scene.coordinate
        if self.scene.draw_on_screen_shift:
            return coord.shift(self.scene.draw_on_screen_shift)
        return coord
