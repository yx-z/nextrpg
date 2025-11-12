from dataclasses import dataclass, replace
from typing import Self, override

from nextrpg.core.time import Millisecond
from nextrpg.scene.scene import Scene
from nextrpg.sound.sound import Sound


@dataclass(frozen=True)
class SceneWithSound(Scene):
    sound: Sound | tuple[Sound, ...] = ()

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if isinstance(self.sound, Sound):
            sound = self.sound.play()
        else:
            sound = tuple(s.play() for s in self.sound)
        return replace(self, sound=sound)

    def stop_sound(self) -> Self:
        if isinstance(self.sound, Sound):
            sound = self.sound.stop()
        else:
            sound = tuple(s.stop() for s in self.sound)
        return replace(self, sound=sound)
