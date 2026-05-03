import pytest
from nextrpg.geometry.size import Width, Height, Size, ZERO_WIDTH, ZERO_HEIGHT, ZERO_SIZE
from nextrpg.geometry.scaling import WidthScaling, HeightScaling, WidthAndHeightScaling
from nextrpg.geometry.coordinate import Coordinate

def test_width_extended():
    w = Width(100)
    # x_axis
    assert w.x_axis.value == 100
    # __mul__ with WidthScaling
    assert (w * WidthScaling(0.5)).value == 50
    # __mul__ with Height -> Size
    s = w * Height(200)
    assert isinstance(s, Size)
    assert s.width_value == 100
    assert s.height_value == 200
    # __truediv__ with Width -> WidthScaling
    ws = w / Width(200)
    assert isinstance(ws, WidthScaling)
    assert ws.value == 0.5
    # __truediv__ with scalar
    assert (w / 2).value == 50
    # __truediv__ with WidthScaling
    assert (w / WidthScaling(2)).value == 50
    # size property
    assert w.size == Size(100, 0)
    # __add__ with Size
    s2 = w + Size(10, 20)
    assert s2 == Size(110, 20)
    # __add__ with Width
    assert (w + Width(10)).value == 110
    # __add__ with scalar
    assert (w + 10).value == 110

def test_height_extended():
    h = Height(100)
    # y_axis
    assert h.y_axis.value == 100
    # __mul__ with HeightScaling
    assert (h * HeightScaling(0.5)).value == 50
    # __mul__ with Width -> Size
    s = h * Width(200)
    assert s == Size(200, 100)
    # __mul__ with scalar
    assert (h * 2).value == 200

def test_size_extended():
    s = Size(100, 200)
    # properties
    assert s.width == Width(100)
    assert s.height == Height(200)
    assert s.negate_width == Size(-100, 200)
    assert s.negate_height == Size(100, -200)
    # __add__ with Coordinate
    assert (s + Coordinate(10, 10)) == Size(110, 210)
    # __mul__ with scalings
    assert s * WidthScaling(2) == Size(200, 200)
    assert s * HeightScaling(2) == Size(100, 400)
    assert s * WidthAndHeightScaling(2) == Size(200, 400)
    assert s * 2 == Size(200, 400)
    assert 2 * s == Size(200, 400)
    # __truediv__
    assert s / WidthScaling(2) == Size(50, 200)
    # str/repr
    assert str(s) == "(100, 200)"
    assert repr(s) == "(100, 200)"
    # coordinate
    assert s.coordinate == Coordinate(100, 200)
    # save/load
    assert s.save_data == s
    assert Size.load_from_save([10, 20]) == Size(10, 20)
    # directional_offset
    assert isinstance(s.directional_offset, object) # Just check it doesn't crash
