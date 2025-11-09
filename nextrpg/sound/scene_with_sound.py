from dataclasses import dataclass, replace
from typing import Self, override

from nextrpg.core.time import Millisecond
from nextrpg.scene.scene import Scene
from nextrpg.sound.sound import Sound, play_optional, stop_optional


@dataclass(frozen=True)
class SceneWithSound(Scene):
    sound: Sound | tuple[Sound, ...] = ()

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if isinstance(self.sound, Sound):
            sound = play_optional(self.sound)
        else:
            sound = tuple(play_optional(s) for s in self.sound)
        return replace(self, sound=sound)

    def stop_sound(self) -> Self:
        if isinstance(self.sound, Sound):
            sound = stop_optional(self.sound)
        else:
            sound = tuple(stop_optional(s) for s in self.sound)
        return replace(self, sound=sound)
