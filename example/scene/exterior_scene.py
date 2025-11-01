from pathlib import Path

from nextrpg import CharacterSpec, MapMove, MapScene


def exterior_scene(player_spec: CharacterSpec) -> MapScene:
    # Local import to avoid circular dependency.
    from example.scene.interior_scene import interior_scene

    tmx = Path("example/asset/exterior.tmx")
    move = MapMove("from_exterior", "to_interior", interior_scene)
    return MapScene(tmx=tmx, player_spec=player_spec, move=move)
