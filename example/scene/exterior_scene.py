from functools import cache

from example.scene.scene_common import SOUND_DIR, TMX_DIR, bgm_config
from nextrpg import MapMove, MapScene, PlayerSpec, Sound, SoundConfig


def exterior_scene(player: PlayerSpec) -> MapScene:
    # Local import to avoid circular dependency.
    from example.scene.interior_scene import interior_scene

    tmx = TMX_DIR / "exterior.tmx"
    move = MapMove("from_exterior", "to_interior", interior_scene)
    return MapScene(tmx=tmx, player_spec=player, move=move, sound=bgm())


@cache
def bgm() -> Sound:
    return Sound(SOUND_DIR / "bgm2.mp3", config=bgm_config())
