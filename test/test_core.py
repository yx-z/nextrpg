from nextrpg.core import Direction, DirectionalOffset, Size


def test_directional_offset() -> None:
    assert DirectionalOffset(Direction.UP, 10).direction is Direction.UP
    assert DirectionalOffset(Direction.UP, 10).offset == 10


def test_size() -> None:
    assert Size(2, 3).scale(2) == Size(4, 6)
