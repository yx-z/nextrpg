from pytest import raises

from nextrpg.core import Direction, DirectionalOffset, Size


def test_directional_offset() -> None:
    assert DirectionalOffset(Direction.UP, 10).direction is Direction.UP
    assert DirectionalOffset(Direction.UP, 10).offset == 10


def test_size() -> None:
    assert Size(2, 3) * 2 == Size(4, 6)
    with raises(ValueError):
        Size(-1, -1)
