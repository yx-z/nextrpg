from pathlib import Path

from nextrpg import (
    AvatarPosition,
    CharacterSpec,
    Color,
    Drawing,
    EventfulScene,
    EventSpec,
    Height,
    MapMove,
    MapScene,
    NpcEventStartMode,
    NpcOnScreen,
    NpcSpec,
    Padding,
    PlayerOnScreen,
    RpgMakerCharacterDrawing,
    RpgMakerSpriteSheet,
    SpriteSheet,
    Text,
    Width,
    config,
    cutscene,
)


def interior_scene(player_spec: CharacterSpec | None = None) -> MapScene:
    if player_spec:
        player = player_spec
    else:
        player = create_player()

    enter_room_spec = EventSpec(enter_room, NpcEventStartMode.COLLIDE)
    auto = NpcSpec(unique_name="Auto", event=enter_room_spec)

    # Local import to avoid circular dependency.
    from example.scene.exterior_scene import exterior_scene

    tmx = Path("example/asset/interior.tmx")
    move = MapMove("from_interior", "to_exterior", exterior_scene)
    priscilla = create_npc("$PixelFantasy_2-Priscilla.png", "Priscilla")
    gale = create_npc("$PixelFantasy_3-Gale.png", "Gale")
    npcs = (priscilla, gale, auto)
    return MapScene(tmx=tmx, player_spec=player, move=move, npc_specs=npcs)


IMG_DIR = Path("example/asset/Pixel Fantasy RMMZ RTP Tiles/img")


def character_drawing(file: str) -> RpgMakerCharacterDrawing:
    path = IMG_DIR / "characters" / file
    drawing = Drawing(path)
    trim = Padding(top=Height(20), left=Width(10), right=Width(10))
    sprite_sheet = RpgMakerSpriteSheet(drawing=drawing, trim=trim)
    return RpgMakerCharacterDrawing(sprite_sheet)


def create_player() -> CharacterSpec:
    character = character_drawing("$PixelFantasy_1-Reid.png")

    avatar_path = IMG_DIR / "faces" / "PixelFantasy-Reid1.png"
    avatar_drawing = Drawing(avatar_path)
    avatar_sprite_sheet = SpriteSheet(
        drawing=avatar_drawing, num_rows=2, num_columns=4
    )
    avatar = avatar_sprite_sheet[0, 0]
    return CharacterSpec(unique_name="Reid", character=character, avatar=avatar)


def create_npc(file: str, name: str) -> NpcSpec:
    character = character_drawing(file)
    return NpcSpec(unique_name=name, character=character, event=greet)


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
    player[AvatarPosition.RIGHT]: f"Hello {npc.name}! I am {player.name}."
