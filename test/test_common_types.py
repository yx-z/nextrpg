from pytest import approx, raises

from nextrpg.common_types import (
    Coordinate,
    Direction,
    PolarVector,
    Rectangle,
    Size,
)


def test_vector() -> None:
    assert PolarVector(Direction.UP, 10).direction is Direction.UP
    assert PolarVector(Direction.UP, 10).offset == 10


def test_coordinate() -> None:
    assert Coordinate(10, 20) * 2 == Coordinate(20, 40)
    assert Coordinate(10, 20) + PolarVector(Direction.UP, 5) == Coordinate(
        10, 15
    )
    assert Coordinate(10, 20) + PolarVector(Direction.DOWN, 5) == Coordinate(
        10, 25
    )
    assert Coordinate(10, 20) + PolarVector(Direction.LEFT, 5) == Coordinate(
        5, 20
    )
    assert Coordinate(10, 20) + PolarVector(Direction.RIGHT, 5) == Coordinate(
        15, 20
    )
    assert Coordinate(10, 20) + PolarVector(Direction.UP_LEFT, 10) == approx(
        Coordinate(2.9289321881345254, 12.928932188134524)
    )
    assert Coordinate(10, 20) + PolarVector(Direction.UP_RIGHT, 10) == approx(
        Coordinate(17.071067811865476, 12.928932188134524)
    )
    assert Coordinate(10, 20) + PolarVector(Direction.DOWN_LEFT, 10) == approx(
        Coordinate(2.9289321881345254, 27.071067811865476)
    )
    assert Coordinate(10, 20) + PolarVector(Direction.DOWN_RIGHT, 10) == approx(
        Coordinate(17.071067811865476, 27.071067811865476)
    )
    with raises(ValueError):
        Coordinate(1, 2) + PolarVector("INVALID_DIRECTION", 1)  # type: ignore


def test_size() -> None:
    assert Size(2, 3) * 2 == Size(4, 6)


def test_rectangle() -> None:
    rect = Rectangle(Coordinate(10, 20), Size(1, 2))
    assert rect.size == Size(1, 2)
    assert rect.left == 10
    assert rect.top == 20
    assert rect.right == 11
    assert rect.bottom == 22
    assert rect.top_left == Coordinate(10, 20)
    assert rect.top_right == Coordinate(11, 20)
    assert rect.bottom_left == Coordinate(10, 22)
    assert rect.bottom_right == Coordinate(11, 22)
    assert rect.top_center == Coordinate(10.5, 20)
    assert rect.bottom_center == Coordinate(10.5, 22)
    assert rect.center_left == Coordinate(10, 21)
    assert rect.center_right == Coordinate(11, 21)
    assert rect.center == Coordinate(10.5, 21)
    assert rect * 2 == Rectangle(Coordinate(20, 40), Size(2, 4))
    assert rect + PolarVector(Direction.UP, 5) == Rectangle(
        Coordinate(10, 15), Size(1, 2)
    )
    rect2 = Rectangle(Coordinate(11, 20), Size(1, 2))
    assert rect.collides(rect2)
    assert Coordinate(10, 20) in rect
