"""
Sample exterior scene.
"""

from nextrpg import CharacterSpec, MapScene, Move


def exterior_scene(player_spec: CharacterSpec) -> MapScene:
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
        moves=Move("from_exterior", "to_interior", interior_scene),
    )
