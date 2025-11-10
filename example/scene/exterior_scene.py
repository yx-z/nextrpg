from functools import cache
from typing import Literal

from example.scene.scene_common import SOUND_DIR, TMX_DIR, bgm_config, sound
from nextrpg import (
    DONT_RESTART_EVENT,
    EventfulScene,
    MapMove,
    MapScene,
    NpcOnScreen,
    NpcSpec,
    PlayerOnScreen,
    PlayerSpec,
    Sound,
)


def exterior_scene(player: PlayerSpec) -> MapScene:
    # Local import to avoid circular dependency.
    from example.scene.interior_scene import interior_scene

    tmx = TMX_DIR / "exterior.tmx"
    move = MapMove("from_exterior", "to_interior", interior_scene)
    fruit = NpcSpec(unique_name="fruit", event=pick_up_fruit)
    return MapScene(
        tmx=tmx, player_spec=player, move=move, npc_specs=fruit, sound=bgm()
    )


def pick_up_fruit(
    player: PlayerOnScreen, npc: NpcOnScreen, scene: EventfulScene
) -> Literal[DONT_RESTART_EVENT]:
    sound().play()
    scene: "You picked up the fruit!"
    return DONT_RESTART_EVENT


@cache
def bgm() -> Sound:
    return Sound(SOUND_DIR / "bgm2.mp3", config=bgm_config())
