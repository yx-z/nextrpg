from nextrpg import CharacterSpec, MapScene, Move


def exterior_scene(player_spec: CharacterSpec) -> MapScene:
    # Local import to avoid circular dependency.
    from interior_scene import interior_scene

    return MapScene(
        tmx_file="example/asset/exterior.tmx",
        player_spec=player_spec,
        move=Move("from_exterior", "to_interior", interior_scene),
    )
