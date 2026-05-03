import pytest
from nextrpg.geometry.coordinate import XAxis, YAxis, Coordinate, ORIGIN
from nextrpg.geometry.size import Width, Height, Size
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.directional_offset import DirectionalOffset
from nextrpg.geometry.direction import Direction

def test_xaxis_extended():
    x = XAxis(10)
    # __sub__ with Width
    assert (x - Width(5)).value == 5
    # __sub__ with XAxis -> returns Width
    res = x - XAxis(2)
    assert isinstance(res, Width)
    assert res.value == 8
    # __matmul__
    coord = x @ YAxis(20)
    assert coord == Coordinate(10, 20)
    # coordinate property
    assert x.coordinate == Coordinate(10, 0)

def test_yaxis_extended():
    y = YAxis(20)
    # height property
    assert y.height == Height(20)
    # __add__ with Height
    assert (y + Height(10)).value == 30
    # __sub__ with Height
    assert (y - Height(5)).value == 15
    # __sub__ with YAxis -> returns Height
    res = y - YAxis(2)
    assert isinstance(res, Height)
    assert res.value == 18
    # __matmul__
    coord = y @ XAxis(10)
    assert coord == Coordinate(10, 20)
    # coordinate property
    assert y.coordinate == Coordinate(0, 20)

def test_coordinate_extended():
    c = Coordinate(10, 20)
    # properties
    assert c.coordinate is c
    assert c.left == XAxis(10)
    assert c.top == YAxis(20)
    assert c.size == Size(10, 20)
    # __neg__
    assert -c == Coordinate(-10, -20)
    # __rmul__
    assert 2 * c == Coordinate(20, 40)
    # __add__ with DirectionalOffset
    do = DirectionalOffset(Direction.RIGHT, 5)
    # DirectionalOffset has a .size property
    assert (c + do) == Coordinate(15, 20)
    # __sub__
    assert (c - Size(5, 5)) == Coordinate(5, 15)
    # relative_to
    assert Coordinate(100, 0).relative_to(ORIGIN) == Direction.RIGHT
    assert Coordinate(0, 100).relative_to(ORIGIN) == Direction.DOWN
    # distance
    assert Coordinate(0, 0).distance(Coordinate(3, 4)) == 5.0
    # str/repr
    assert str(c) == "(10, 20)"
    assert repr(c) == "(10, 20)"

def test_anchor_negation():
    # In nextrpg/geometry/anchor.py, __neg__ is a @cached_property
    for a in Anchor:
        # Accessing the property calls the method
        assert isinstance(a.__neg__, Anchor)

def test_sizable_proxy_methods():
    from nextrpg.geometry.size import Size
    from nextrpg.geometry.coordinate import Coordinate
    size = Size(100, 100)
    pos = Coordinate(50, 50)
    
    # Test all the "as_..._of" methods
    assert pos.as_top_left_of(size).top_left == pos
    assert pos.as_top_center_of(size).top_left == Coordinate(0, 50)
    assert pos.as_top_right_of(size).top_left == Coordinate(-50, 50)
    assert pos.as_center_left_of(size).top_left == Coordinate(50, 0)
    assert pos.as_center_of(size).top_left == Coordinate(0, 0)
    assert pos.as_center_right_of(size).top_left == Coordinate(-50, 0)
    assert pos.as_bottom_left_of(size).top_left == Coordinate(50, -50)
    assert pos.as_bottom_center_of(size).top_left == Coordinate(0, -50)
    assert pos.as_bottom_right_of(size).top_left == Coordinate(-50, -50)
