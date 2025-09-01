from pathlib import Path

from nextrpg import CharacterSpec, MapScene, Move


def exterior_scene(player_spec: CharacterSpec) -> MapScene:
    # Local import to avoid circular dependency.
    from interior_scene import interior_scene

    tmx = Path("example/asset/exterior.tmx")
    move = Move("from_exterior", "to_interior", interior_scene)
    return MapScene(tmx_file=tmx, player_spec=player_spec, move=move)
