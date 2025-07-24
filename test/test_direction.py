from nextrpg import Direction, DirectionalOffset


def test_directional_offset() -> None:
    assert -DirectionalOffset(Direction.UP, 10) == DirectionalOffset(
        Direction.DOWN, 10
    )
