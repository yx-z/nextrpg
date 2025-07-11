"""
Sample interior scene.
"""

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterSpec
from nextrpg.character.npcs import EventfulScene, NpcOnScreen, NpcSpec
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.character.rpg_maker_character_drawing import (
    Trim,
    RpgMakerCharacterDrawing,
    SpriteSheet,
    SpriteSheetSelection,
)
from nextrpg.core import Direction
from nextrpg.draw.draw_on_screen import Drawing
from nextrpg.event.plugins import say
from nextrpg.scene.map_scene import MapScene, Move
from nextrpg.scene.scene import Scene


def interior_scene(player_spec: CharacterSpec | None = None) -> Scene:
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
        moves=(Move("from_interior", "to_exterior", exterior_scene),),
        # NPC/events.
        npc_specs=(
            NpcSpec(name="david", character=david(), event=greet),
            NpcSpec(name="alisa", character=alisa(), event=greet),
        ),
    )


def greet(
    player: PlayerOnScreen,
    npc: NpcOnScreen,
    npc_dict: dict[str, NpcOnScreen],
    scene: EventfulScene,
) -> None:
    """
    Greet event specification.

    Arguments:
        `player`: Player.

        `npc`: The triggerd NPC.

        `npc_dict`: Dictionary of NPCs in the scene.

        `scene`: The scene that triggered the event.
    Returns:
        `None`
    """
    player: f"Hello {npc.spec.name}!"
    npc: f"Hello {player.spec.name}!"

    other_npc = {
        "david": npc_dict["alisa"],
        "alisa": npc_dict["david"],
    }[npc.spec.name]
    other_npc: f"Hello, I am {other_npc.spec.name}!"


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
        name="player",
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
