from dataclasses import dataclass, replace
from typing import Self, override

from nextrpg.core.time import Millisecond
from nextrpg.game.game_state import GameState
from nextrpg.scene.scene import Scene
from nextrpg.sound.sound import Sound


@dataclass(frozen=True)
class SceneWithSound(Scene):
    sound: Sound | tuple[Sound, ...] = ()

    @override
    def tick(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Self, GameState]:
        if isinstance(self.sound, Sound):
            sound = self.sound.play()
        else:
            sound = tuple(s.play() for s in self.sound)
        ticked = replace(self, sound=sound)
        return ticked, state

    def stop_sound(self) -> Self:
        if isinstance(self.sound, Sound):
            sound = self.sound.stop()
        else:
            sound = tuple(s.stop() for s in self.sound)
        return replace(self, sound=sound)
