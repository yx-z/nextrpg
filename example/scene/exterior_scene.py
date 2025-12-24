from typing import Literal

from example.item.item import ItemKey
from example.scene.scene_common import AUDIO_DIR, TMX_DIR, alert_sound
from nextrpg import (
    DISMISS_EVENT,
    EventfulScene,
    GameState,
    MapMove,
    MapSpec,
    MusicSpec,
    NpcOnScreen,
    NpcSpec,
    PlayerOnScreen,
    PlayerSpec,
    Text,
    config,
)


def exterior_scene(player: PlayerSpec, state: GameState) -> MapSpec:
    # Local import to avoid circular dependency.
    from example.scene.interior_scene import interior_scene

    return MapSpec(
        tmx=TMX_DIR / "exterior.tmx",
        player=player,
        npc=NpcSpec(unique_name="fruit", event=pick_up_fruit),
        move=MapMove("from_exterior", "to_interior", interior_scene),
        music=MusicSpec(AUDIO_DIR / "bgm2.mp3"),
    )


def pick_up_fruit(
    player: PlayerOnScreen,
    fruit: NpcOnScreen,
    scene: EventfulScene,
    state: GameState,
) -> Literal[DISMISS_EVENT]:
    alert_sound().play()
    scene.fade_out_character(fruit)

    cfg = config().event.say_event.text_config
    icon = config().rpg.item.get_icon(ItemKey.FRUIT) or ""
    scene: Text("You picked up the fruit! ", cfg) + icon

    state.update_event(inventory_update=ItemKey.FRUIT)
    return DISMISS_EVENT
