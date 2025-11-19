from functools import cache
from typing import Literal

from example.item.item import ItemKey
from example.scene.scene_common import SOUND_DIR, TMX_DIR, bgm_config, sound
from nextrpg import (
    DISMISS_EVENT,
    EventfulScene,
    GameState,
    MapMove,
    MapScene,
    NpcOnScreen,
    NpcSpec,
    PlayerOnScreen,
    PlayerSpec,
    Sound,
)


def exterior_scene(player: PlayerSpec, state: GameState) -> MapScene:
    # Local import to avoid circular dependency.
    from example.scene.interior_scene import interior_scene

    tmx = TMX_DIR / "exterior.tmx"
    move = MapMove("from_exterior", "to_interior", interior_scene)
    fruit = NpcSpec(unique_name="fruit", event=pick_up_fruit)
    return MapScene(
        tmx=tmx, player_spec=player, move=move, npc_specs=fruit, sound=bgm()
    )


def pick_up_fruit(
    player: PlayerOnScreen,
    fruit: NpcOnScreen,
    scene: EventfulScene,
    state: GameState,
) -> Literal[DISMISS_EVENT]:
    sound().play()
    scene.fade_out_character(fruit)
    scene: "You picked up the fruit!"
    state.update_event(inventory_update=+ItemKey.FRUIT)
    return DISMISS_EVENT


@cache
def bgm() -> Sound:
    return Sound(SOUND_DIR / "bgm2.mp3", loop=True, config=bgm_config())
