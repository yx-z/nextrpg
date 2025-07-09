"""
Sample exterior scene.
"""

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterSpec
from nextrpg.event.move import Move
from nextrpg.scene.map_scene import MapScene
from nextrpg.scene.scene import Scene


def exterior_scene(player_spec: CharacterSpec) -> Scene:
    """
    Arguments:
        `player_spec`: Character drawing and name to use for the player.

    Returns:
        `Scene`: The exterior scene.
    """
    # Local import to avoid circular dependency.
    from interior_scene import interior_scene

    return MapScene(
        # Tiled/tmx tile map .
        tmx_file="example/assets/exterior.tmx",
        # Reuse the same character drawing from the previous map.
        player_spec=player_spec,
        # Move to another map.
        moves=(Move("from_exterior", "to_interior", interior_scene),),
    )
