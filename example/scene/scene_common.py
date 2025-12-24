from functools import cache
from pathlib import Path

from nextrpg import Sound, SoundSpec

THIS_DIR = Path(__file__).parent
IMG_DIR = THIS_DIR / "Pixel Fantasy RMMZ RTP Tiles" / "img"
TMX_DIR = THIS_DIR / "tmx"
AUDIO_DIR = THIS_DIR / "audio"


@cache
def alert_sound() -> Sound:
    sound_spec = SoundSpec(AUDIO_DIR / "alert.mp3")
    return Sound(sound_spec)
