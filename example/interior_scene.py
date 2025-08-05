from nextrpg import (
    ORIGIN,
    CharacterDraw,
    CharacterSpec,
    Color,
    Coordinate,
    Direction,
    Draw,
    EventfulScene,
    MapScene,
    Move,
    NpcOnScreen,
    NpcSpec,
    PlayerOnScreen,
    RectangleOnScreen,
    RpgMakerCharacterDraw,
    RpgMakerSpriteSheet,
    Selection,
    Size,
    Text,
    Trim,
    config,
    fade_in,
    fade_out,
    gui_size,
    register_rpg_event,
)


def interior_scene(player_spec: CharacterSpec | None = None) -> MapScene:
    # Local import to avoid circular dependency.
    from exterior_scene import exterior_scene

    return MapScene(
        "example/asset/interior.tmx",
        player_spec or init_player(),
        Move("from_interior", "to_exterior", exterior_scene),
        (
            NpcSpec("david", david(), event=greet_with_cutscene),
            NpcSpec("alisa", alisa(), event=greet_with_cutscene),
        ),
    )


def greet_with_cutscene(
    player: PlayerOnScreen, npc: NpcOnScreen, scene: EventfulScene
) -> None:
    gui_width, gui_height = gui_size()
    cfg = config().cutscene
    rect_height = gui_height * cfg.screen_height_percentage
    size = Size(gui_width, rect_height)
    top_border = RectangleOnScreen(ORIGIN, size)
    bottom_coord = Coordinate(0, gui_height - rect_height)
    bottom_border = RectangleOnScreen(bottom_coord, size)
    borders = tuple(r.fill(cfg.background) for r in (top_border, bottom_border))

    sentinel = fade_in(borders, cfg.wait, cfg.duration)
    greet(player, npc, scene)
    fade_out(sentinel, cfg.wait, cfg.duration)


@register_rpg_event
def greet(
    player: PlayerOnScreen, npc: NpcOnScreen, scene: EventfulScene
) -> None:
    npc: "Nice to meet you! What's your name?"
    player: f"Hello {npc.display_name}! I am {player.display_name}."
    npc: f"Hello {player.display_name}!"

    other_name = "david" if npc.display_name == "alisa" else "alisa"
    other_npc = scene.get_character(other_name)
    other_npc: f"Hello! I am {other_npc.display_name}!"

    cfg = config().say_event.text_config
    # fmt: off
    scene["Interior Scene"]: Text("Greetings!", cfg.sized(40)) + Text(
"""This is...
a sample """, cfg) + Text("nextrpg event", cfg.colored(Color(128, 0, 255)))
    # fmt: on


def sprite_sheet() -> RpgMakerSpriteSheet:
    return RpgMakerSpriteSheet(
        resource="example/asset/Characters_MV.png", trim=Trim(top=25)
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
        avatar=Draw("example/asset/avatar.png"),
    )


def alisa() -> CharacterDraw:
    return RpgMakerCharacterDraw(
        Direction.RIGHT, sprite_sheet(), Selection(row=0, column=1)
    )


def david() -> CharacterDraw:
    return RpgMakerCharacterDraw(
        Direction.DOWN, sprite_sheet(), Selection(row=0, column=2)
    )
