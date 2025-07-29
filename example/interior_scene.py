from nextrpg import (
    CharacterDraw,
    CharacterSpec,
    Direction,
    EventfulScene,
    MapScene,
    Move,
    NpcOnScreen,
    NpcSpec,
    PlayerOnScreen,
    RpgMakerCharacterDraw,
    RpgMakerSpriteSheet,
    Selection,
    Trim,
)


def interior_scene(player_spec: CharacterSpec | None = None) -> MapScene:
    # Local import to avoid circular dependency.
    from exterior_scene import exterior_scene

    return MapScene(
        "example/assets/interior.tmx",
        player_spec or init_player(),
        Move("from_interior", "to_exterior", exterior_scene),
        (
            NpcSpec(object_name="david", character=david(), event=greet),
            NpcSpec(object_name="alisa", character=alisa(), event=greet),
        ),
    )


def greet(
    player: PlayerOnScreen, npc: NpcOnScreen, scene: EventfulScene
) -> None:
    npc: "Nice to meet you! What's your name?"
    player: f"Hello {npc.display_name}! I am {player.display_name}."
    npc: f"Hello {player.display_name}!"

    other_name = "david" if npc.display_name == "alisa" else "alisa"
    other_npc = scene.get_npc(other_name)
    other_npc: f"Hello! I am {other_npc.display_name}!"

    # fmt: off
    scene["Name"]: """Greetings!
    This is...

    a sample nextrpg event. :)"""
    # fmt: on


def sprite_sheet() -> RpgMakerSpriteSheet:
    return RpgMakerSpriteSheet(
        resource="example/assets/Characters_MV.png", trim=Trim(top=25)
    )


def init_player() -> CharacterSpec:
    return CharacterSpec(
        object_name="player",
        display_name="Will",
        character=RpgMakerCharacterDraw(
            Direction.DOWN,
            sprite_sheet(),
            Selection(row=0, column=0),
        ),
    )


def alisa() -> CharacterDraw:
    return RpgMakerCharacterDraw(
        Direction.RIGHT, sprite_sheet(), Selection(row=0, column=1)
    )


def david() -> CharacterDraw:
    return RpgMakerCharacterDraw(
        Direction.DOWN, sprite_sheet(), Selection(row=0, column=2)
    )
