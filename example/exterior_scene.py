from pathlib import Path

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.event.move import Move
from nextrpg.scene.map_scene import MapScene
from nextrpg.scene.scene import Scene


def exterior_scene(
    player: CharacterDrawing, player_coordinate_object: str
) -> Scene:
    """
    Arguments:
        `player`: The character drawing to use for the player.

        `player_coordinate_object`: Name of the object to use as the player.

    Returns:
        `Scene`: The exterior scene.
    """
    # Local import to avoid circular dependency.
    from example.interior_scene import interior_scene

    return MapScene(
        # Tiled/tmx tile map .
        Path("example/assets/exterior.tmx"),
        # Reuse the same character drawing from the previous map.
        player,
        # Player coordinate on the map.
        player_coordinate_object,
        # Move to another map.
        [Move("from_exterior", "to_interior", interior_scene)],
    )
