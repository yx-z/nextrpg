from __future__ import annotations

from dataclasses import dataclass

from nextrpg.character.npc_on_screen import NpcEventGenerator
from nextrpg.scene.eventful_scene import EventfulScene
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class RpgEventScene(Scene):
    generator: NpcEventGenerator
    scene: EventfulScene
