"""
Sample interior scene.
"""

from typing import Any

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.moving_npc import MovingNpcSpec
from nextrpg.character.npcs import NpcSpec
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.character.rpg_maker_character_drawing import (
    Margin,
    RpgMakerCharacterDrawing,
    SpriteSheet,
    SpriteSheetSelection,
)
from nextrpg.core import Direction
from nextrpg.draw_on_screen import Drawing
from nextrpg.event.move import Move
from nextrpg.event.say import say
from nextrpg.scene.map_scene import MapScene
from nextrpg.scene.scene import Scene


def interior_scene(
    player: CharacterDrawing | None = None,
    player_coordinate_object: str = "player",
) -> Scene:
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
        initial_player_drawing=player or init_player(),
        # Player coordinate on the map.
        player_coordinate_object=player_coordinate_object,
        # Move to another map.
        moves=(Move("from_interior", "to_exterior", exterior_scene),),
        # NPC/events.
        npc_specs=(
            NpcSpec(name="david", character=david(), event=greet),
            MovingNpcSpec(name="alisa", character=alisa(), event=greet),
        ),
    )


def greet(player: PlayerOnScreen, *args: Any) -> None:
    """
    Greet event specification.

    Arguments:
        `player`: Player.

    Returns:
        `None`
    """
    say(player, "Hello World!")


def sprite_sheet() -> SpriteSheet:
    """
    Load the character sprite sheet.

    Returns:
        `SpriteSheet`: The sprite sheet.
    """
    return SpriteSheet(
        # Player sprite sheet.
        Drawing("example/assets/Characters_MV.png"),
        # Declare margins to correctly detect collision/bounding box.
        Margin(top=25),
    )


def init_player() -> CharacterDrawing:
    """
    Initialize the player drawing.

    Returns:
        `CharacterDrawing`: The player character drawing.
    """
    return RpgMakerCharacterDrawing(
        direction=Direction.DOWN,
        sprite_sheet=sprite_sheet(),
        # Select a character from the sprite sheet.
        sprite_sheet_selection=SpriteSheetSelection(row=0, column=0),
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
