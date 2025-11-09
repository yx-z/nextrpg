from pathlib import Path

from nextrpg import SoundConfig

THIS_DIR = Path(__file__).parent
IMG_DIR = THIS_DIR / "Pixel Fantasy RMMZ RTP Tiles" / "img"
TMX_DIR = THIS_DIR / "tmx"
SOUND_DIR = THIS_DIR / "sound"


def bgm_config() -> SoundConfig:
    return SoundConfig(fade_in_duration=1600, fade_out_duration=800)
