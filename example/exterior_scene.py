from pathlib import Path

from example.common import create_player
from nextrpg import CharacterSpec, MapMove, MapScene


def exterior_scene(player_spec: CharacterSpec | None = None) -> MapScene:
    if player_spec:
        player = player_spec
    else:
        player = create_player()

    # Local import to avoid circular dependency.
    from interior_scene import interior_scene

    tmx = Path("example/asset/exterior.tmx")
    move = MapMove("from_exterior", "to_interior", interior_scene)
    return MapScene(tmx_file=tmx, player_spec=player, move=move)
