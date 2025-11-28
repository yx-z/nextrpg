from example.item.item import ItemKey
from example.scene.scene_common import SOUND_DIR, TMX_DIR, bgm_config, sound
from nextrpg import (
    EventfulScene,
    GameState,
    MapMove,
    MapScene,
    NpcOnScreen,
    NpcSpec,
    PlayerOnScreen,
    PlayerSpec,
    Sound,
    Text,
    config,
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
) -> None:
    sound().play()

    cfg = config().event.say_event.text_config
    icon = config().item.get_icon(ItemKey.FRUIT)
    scene: (
        Text("You picked up the fruit! ", cfg) + icon + Text("\nTry it!", cfg)
    )

    state.update_event(inventory_update=+ItemKey.FRUIT)


def bgm() -> Sound:
    return Sound(SOUND_DIR / "bgm2.mp3", loop=True, config=bgm_config())
