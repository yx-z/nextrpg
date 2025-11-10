from dataclasses import dataclass, replace
from typing import Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.core.time import Millisecond
from nextrpg.event.eventful_scene import EventfulScene
from nextrpg.event.rpg_event_scene import (
    RpgEventScene,
    register_rpg_event_scene,
)
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class UpdateFromEvent(RpgEventScene):
    character_or_scene: CharacterOnScreen | Scene

    @override
    def _tick_after_parent(
        self, time_delta: Millisecond, ticked: Self
    ) -> Scene:
        if isinstance(scene := self.character_or_scene, Scene):
            return scene.complete(self.generator)
        if (character := self.character_or_scene).has_same_name(
            self.parent.player
        ):
            scene = replace(self.parent, player=character)
            return scene.complete(self.generator)
        npcs = tuple(
            character if character.has_same_name(n) else n
            for n in self.parent.npcs
        )
        scene = replace(self.parent, npcs=npcs)
        return scene.complete(self.generator)


@register_rpg_event_scene(UpdateFromEvent)
def update_from_event(
    character_or_scene: CharacterOnScreen | EventfulScene,
) -> None: ...
