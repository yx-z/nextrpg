"""
Sample interior scene.
"""

from nextrpg import (
    CharacterDrawing,
    CharacterSpec,
    Drawing,
    EventfulScene,
    MapScene,
    Move,
    NpcOnScreen,
    NpcSpec,
    PlayerOnScreen,
    RpgMakerCharacterDrawing,
    Scene,
    SpriteSheet,
    SpriteSheetSelection,
    Trim,
    Direction,
)


def interior_scene(player_spec: CharacterSpec | None = None) -> MapScene:
    """
    Defines an interior scene.

    Arguments:
        `player`: Character drawing to use for the player.
            If `None`, a default character drawing is used.
            This allows the interior_scene to be used as the entry_scene for
            `nextrpg.Game(entry_scene)`.

        `player_coordinate_object`: Name of the object marking the initial
            coordinate of the player.

    Returns:
        `Scene`: The interior scene.
    """
    # Local import to avoid circular dependency.
    from exterior_scene import exterior_scene

    return MapScene(
        # Tiled/tmx tile map.
        tmx_file="example/assets/interior.tmx",
        # Use default player drawing when this scene is an entry scene.
        player_spec=player_spec or init_player(),
        # Move to another map.
        moves=Move("from_interior", "to_exterior", exterior_scene),
        # NPC/events.
        npc_specs=(
            NpcSpec(object_name="david", character=david(), event=greet),
            NpcSpec(object_name="alisa", character=alisa(), event=greet),
        ),
    )


def greet(
    player: PlayerOnScreen, npc: NpcOnScreen, scene: EventfulScene
) -> None:
    """
    Greet event specification.

    Arguments:
        `player`: Player.

        `npc`: The triggerd NPC.

        `scene`: The scene that triggered the event.

    Returns:
        `None`
    """
    scene: "Greetings! This is a sample nextrpg event."

    npc: "Nice to meet you! What's your name?"
    player: f"Hello {npc.name}! I am {player.name}."
    npc: f"Hello {player.name}!"

    other_npc = scene.npc_dict["david" if npc.name == "alisa" else "alisa"]
    other_npc: f"Hello! I am {other_npc.name}!"


def sprite_sheet() -> SpriteSheet:
    """
    Load the character sprite sheet.

    Returns:
        `SpriteSheet`: The sprite sheet.
    """
    return SpriteSheet(
        # Player sprite sheet.
        Drawing("example/assets/Characters_MV.png"),
        # Declare trims to correctly detect collision/bounding box.
        Trim(top=25),
    )


def init_player() -> CharacterSpec:
    """
    Initialize the player drawing.

    Returns:
        `CharacterSpec`: The player name and drawing.
    """
    return CharacterSpec(
        # Name of the object on the Tiled/tmx map.
        object_name="player",
        display_name="Will",
        character=RpgMakerCharacterDrawing(
            direction=Direction.DOWN,
            sprite_sheet=sprite_sheet(),
            # Select a character from the sprite sheet.
            sprite_sheet_selection=SpriteSheetSelection(row=0, column=0),
        ),
    )


def alisa() -> CharacterDrawing:
    """
    Initialize the NPC Alisa's drawing.

    Returns:
        `CharacterDrawing`: The NPC Alisa's character drawing.
    """
    return RpgMakerCharacterDrawing(
        direction=Direction.RIGHT,
        sprite_sheet=sprite_sheet(),
        sprite_sheet_selection=SpriteSheetSelection(0, 1),
    )


def david() -> CharacterDrawing:
    """
    Initialize the NPC David's drawing.

    Returns:
        `CharacterDrawing`: The NPC David's character drawing.
    """
    return RpgMakerCharacterDrawing(
        direction=Direction.DOWN,
        sprite_sheet=sprite_sheet(),
        sprite_sheet_selection=SpriteSheetSelection(0, 2),
    )
