from pathlib import Path

from nextrpg import (
    CharacterSpec,
    Color,
    Direction,
    Drawing,
    DrawingTrim,
    EventfulScene,
    EventSpec,
    Height,
    MapScene,
    Move,
    NpcEventStartMode,
    NpcOnScreen,
    NpcSpec,
    PlayerOnScreen,
    RpgMakerCharacterDrawing,
    RpgMakerSpriteSheet,
    SpriteSheetSelection,
    Text,
    config,
    cutscene,
)


def interior_scene(player_spec: CharacterSpec | None = None) -> MapScene:
    sprite_sheet_drawing = Drawing(Path("example/asset/Characters_MV.png"))
    sprite_sheet_trim = DrawingTrim(top=Height(25))
    sprite_sheet = RpgMakerSpriteSheet(
        drawing=sprite_sheet_drawing, trim=sprite_sheet_trim
    )

    if player_spec:
        player = player_spec
    else:
        player_drawing = RpgMakerCharacterDrawing(
            Direction.DOWN,
            sprite_sheet,
            SpriteSheetSelection(row=0, column=0),
        )
        avatar = Drawing(Path("example/asset/avatar.png"))
        player = CharacterSpec(
            unique_name="player",
            display_name="Will",
            character=player_drawing,
            avatar=avatar,
        )

    alisa_drawing = RpgMakerCharacterDrawing(
        Direction.RIGHT, sprite_sheet, SpriteSheetSelection(row=0, column=1)
    )
    alisa = NpcSpec(unique_name="alisa", character=alisa_drawing, event=greet)

    david_drawing = RpgMakerCharacterDrawing(
        Direction.DOWN, sprite_sheet, SpriteSheetSelection(row=0, column=2)
    )
    david = NpcSpec(unique_name="david", character=david_drawing, event=greet)

    enter_room_spec = EventSpec(enter_room, NpcEventStartMode.COLLIDE)
    auto_trigger = NpcSpec(unique_name="auto", event=enter_room_spec)

    # Local import to avoid circular dependency.
    from exterior_scene import exterior_scene

    tmx = Path("example/asset/interior.tmx")
    move = Move("from_interior", "to_exterior", exterior_scene)
    npcs = (david, alisa, auto_trigger)
    return MapScene(tmx_file=tmx, player_spec=player, move=move, npc_specs=npcs)


def enter_room(
    player: PlayerOnScreen, npc: NpcOnScreen, scene: EventfulScene
) -> bool:
    scene: "You've entered this room!"
    return False


@cutscene
def greet(
    player: PlayerOnScreen, npc: NpcOnScreen, scene: EventfulScene
) -> None:
    cfg = config().say_event.text_config
    # fmt: off
    scene["Interior Scene"]: Text("Greetings!", cfg.sized(Height(40))) + Text(
        """This is...
        a sample """, cfg) + Text("nextrpg event", cfg.colored(Color(128, 0, 255)))
    # fmt: on

    npc: "Nice to meet you! What's your name?"
    player: f"Hello {npc.display_name}! I am {player.display_name}."
    npc: f"Hello {player.display_name}!"

    other_name = "david" if npc.display_name == "alisa" else "alisa"
    other_npc = scene.get_character(other_name)
    other_npc: f"Hello! I am {other_npc.display_name}!"
