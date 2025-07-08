from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npcs import RpgEventScene
from nextrpg.coordinate import Coordinate
from nextrpg.core import Millisecond
from nextrpg.draw_on_screen import DrawOnScreen
from nextrpg.event.pygame_event import KeyPressDown, KeyboardKey, PygameEvent
from nextrpg.event.rpg_event import register_rpg_event
from nextrpg.scene.map_scene import MapScene
from nextrpg.scene.scene import Scene
from nextrpg.text import Text


@register_rpg_event
def say(character: CharacterOnScreen, message: str) -> None:
    """
    Character says a message.

    Arguments:
        `character`: The character to say something.

        `message`: The message to say.

    Returns:
        Type-hinted type: `None`. For user code (RpgEventSpec), `say` returns
            no result (from the ` SayEvent ` scene).
        Actual type: `RpgEventCallable`. For `Npcs`/`MapScene` to yield the
            scene coroutine.
    """
    return lambda generator, scene: SayEvent(
        generator, scene, character, message
    )


@dataclass(frozen=True)
class SayEvent(RpgEventScene):
    """
    `say` scene.

    Arguments:
        `character`: The character to say the message.

        `message`: The message to say.
    """

    character: CharacterOnScreen
    message: str

    @cached_property
    @override
    def _draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        return self._scene.draw_on_screens_shifted + (
            Text(self.message, self._coordinate).draw_on_screen,
        )

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        return replace(self, _scene=self._scene.tick(time_delta))

    @override
    def event(self, e: PygameEvent) -> Scene:
        if isinstance(e, KeyPressDown):
            return (
                self._scene.send(self._generator)
                if e.key is KeyboardKey.CONFIRM
                else self
            )
        return replace(self, _scene=self._scene.event(e))

    @cached_property
    def _coordinate(self) -> Coordinate:
        coord = self.character.coordinate
        return (
            coord.shift(self._scene.draw_on_screen_shift)
            if isinstance(self._scene, MapScene)
            else coord
        )
