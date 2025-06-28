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
from nextrpg.draw_on_screen import Drawing
from nextrpg.event.move import Move
from nextrpg.scene.map_scene import MapScene
from nextrpg.scene.scene import Scene


def interior_scene(
    player: CharacterDrawing | None = None,
    player_coordinate_object: str | None = None,
) -> Scene:
    """
    Defines an interior scene.

    Arguments:
        `player`: Character drawing to use for the player.
            If `None`, a default character drawing is used.
            This allows the interior_scene to be used as the entry_scene for
            `nextrpg.Game(entry_scene)`.

        `player_coordinate_object`: Name of the object marking the initial
            coordinate of the player. If `None`, the player is placed at the
            object location with the name `config().map.player` in the map.

    Returns:
        `Scene`: The interior scene.
    """
    # Local import to avoid circular dependency.
    from example.exterior_scene import exterior_scene

    return MapScene(
        # Tiled/tmx tile map.
        Path("example/assets/interior.tmx"),
        # Create character drawing when this scene is an entry scene.
        player or _create_character(),
        # Player coordinate on the map.
        player_coordinate_object,
        # Move to another map.
        [Move("from_interior", "to_exterior", exterior_scene)],
    )


def _create_character() -> CharacterDrawing:
    return RpgMakerCharacterDrawing(
        SpriteSheet(
            # Player sprite sheet.
            Drawing(Path("example/assets/fantasy/FCharacter1.png")),
            # Select a character from the sprite sheet.
            SpriteSheetSelection(row=0, column=1),
            # Declare margins to correctly detect collision/bounding box.
            margin=Margin(top=22, left=8, right=8),
        )
    )
