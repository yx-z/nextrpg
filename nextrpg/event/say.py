from dataclasses import dataclass, replace
from functools import cached_property, singledispatchmethod

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npcs import RpgEventGenerator
from nextrpg.draw_on_screen import Coordinate, DrawOnScreen
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


@dataclass
class SayEvent(Scene):
    """
    `say` scene.

    Arguments:
        `generator`: The generator to continue after the event.

        `scene`: The scene to continue.

        `character`: The character to say the message.

        `message`: The message to say.
    """

    generator: RpgEventGenerator
    scene: MapScene
    character: CharacterOnScreen
    message: str

    @cached_property
    def draw_on_screens(self) -> list[DrawOnScreen]:
        return self.scene.draw_on_screens + [
            Text(self.message, Coordinate(200, 200)).draw_on_screen
        ]

    @singledispatchmethod
    def event(self, e: PygameEvent) -> Scene:
        return self

    @event.register
    def _confirm(self, e: KeyPressDown) -> Scene:
        if e.key is KeyboardKey.CONFIRM:
            return replace(self.scene, _ongoing_event=self.generator)
        return self
