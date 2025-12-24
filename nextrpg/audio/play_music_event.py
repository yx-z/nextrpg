from dataclasses import dataclass

from pygame import mixer_music

from nextrpg.audio.music_spec import MusicSpec
from nextrpg.core.util import background_thread
from nextrpg.event.user_event import UserEvent


@dataclass(frozen=True)
class PlayMusicEvent(UserEvent):
    spec: MusicSpec

    def __call__(self) -> None:
        background_thread().submit(self._play)

    def _play(self) -> None:
        mixer_music.load(self.spec.file)
        mixer_music.play(
            self.spec.loop_flag, fade_ms=self.spec.config.fade_in_duration
        )
