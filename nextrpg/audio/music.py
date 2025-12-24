from pygame import mixer_music

from nextrpg.audio.music_spec import MusicSpec
from nextrpg.audio.play_music_event import PlayMusicEvent
from nextrpg.event.user_event import post_user_event


def play_music(spec: MusicSpec | None) -> None:
    global _playing
    if not spec or _playing == spec:
        return

    if _playing:
        delay = _playing.config.fade_out_duration
        stop_music()
    else:
        delay = 0
    _playing = spec
    event = PlayMusicEvent(spec)
    post_user_event(event, delay=delay)


def stop_music() -> None:
    global _playing
    if _playing:
        mixer_music.fadeout(_playing.config.fade_out_duration)
        _playing = None


_playing: MusicSpec | None = None
