from collections.abc import Callable, Generator
from dataclasses import dataclass, replace
from functools import cached_property, singledispatchmethod

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.draw_on_screen import Coordinate, DrawOnScreen
from nextrpg.event.pygame_event import KeyPressDown, KeyboardKey, PygameEvent
from nextrpg.scene.map_scene import MapScene
from nextrpg.scene.scene import Scene
from nextrpg.text import Text


def say(
    player: CharacterOnScreen, message: str
) -> Generator[Callable[[Generator, Scene], Scene], None, None]:
    yield lambda generator, scene: SayEvent(generator, scene, player, message)


@dataclass
class SayEvent(Scene):
    generator: Generator
    scene: MapScene
    player: CharacterOnScreen
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
            return replace(self.scene, _current_event=self.generator)
        return self
