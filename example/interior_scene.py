"""
Sample scene.
"""

from pathlib import Path

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.rpg_maker_character_drawing import (
    Margin,
    RpgMakerCharacterDrawing,
    SpriteSheet,
    SpriteSheetSelection,
)
from nextrpg.core import Direction
from nextrpg.draw_on_screen import Drawing
from nextrpg.event.move import Move
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
    from example.exterior_scene import exterior_scene

    return MapScene(
        # Tiled/tmx tile map.
        Path("example/assets/interior.tmx"),
        # Create character drawing when this scene is an entry scene.
        player or _init_player(),
        # Player coordinate on the map.
        player_coordinate_object,
        # Move to another map.
        [Move("from_interior", "to_exterior", exterior_scene)],
        [],
    )


def _init_player() -> CharacterDrawing:
    return RpgMakerCharacterDrawing(
        Direction.DOWN,
        SpriteSheet(
            # Player sprite sheet.
            Drawing("example/assets/Characters_MV.png"),
            # Select a character from the sprite sheet.
            SpriteSheetSelection(row=0, column=1),
            # Declare margins to correctly detect collision/bounding box.
            margin=Margin(top=25),
        ),
    )
