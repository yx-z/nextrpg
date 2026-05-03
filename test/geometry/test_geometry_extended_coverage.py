import pytest
from nextrpg.geometry.scaling import WidthScaling, HeightScaling, WidthAndHeightScaling
from nextrpg.geometry.size import Width, Height, Size
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.polygon_area_on_screen import PolygonAreaOnScreen
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen

def test_scaling_complement():
    ws = WidthScaling(0.3)
    assert ws.complement.value == pytest.approx(0.7)
    hs = HeightScaling(0.4)
    assert hs.complement.value == pytest.approx(0.6)
    whs = WidthAndHeightScaling(0.5)
    assert whs.complement.value == pytest.approx(0.5)

def test_scaling_multiplication():
    ws = WidthScaling(0.5)
    assert (ws * 2).value == 1.0
    assert (ws * Width(100)).value == 50
    
    hs = HeightScaling(0.5)
    assert (hs * 2).value == 1.0
    assert (hs * Height(100)).value == 50
    
    whs = WidthAndHeightScaling(0.5)
    assert (whs * 2).value == 1.0
    s = whs * Size(100, 200)
    assert s.width_value == 50
    assert s.height_value == 100

def test_polygon_collision():
    p1 = PolygonAreaOnScreen((
        Coordinate(0, 0), Coordinate(10, 0), Coordinate(10, 10), Coordinate(0, 10)
    ))
    p2 = PolygonAreaOnScreen((
        Coordinate(5, 5), Coordinate(15, 5), Coordinate(15, 15), Coordinate(5, 15)
    ))
    assert p1.collide(p2) is True
    
    p3 = PolygonAreaOnScreen((
        Coordinate(20, 20), Coordinate(30, 20), Coordinate(30, 30), Coordinate(20, 30)
    ))
    assert p1.collide(p3) is False

def test_polygon_contains_area():
    p1 = PolygonAreaOnScreen((
        Coordinate(0, 0), Coordinate(10, 0), Coordinate(10, 10), Coordinate(0, 10)
    ))
    p_inside = PolygonAreaOnScreen((
        Coordinate(2, 2), Coordinate(8, 2), Coordinate(8, 8), Coordinate(2, 8)
    ))
    assert (p_inside in p1) is True

def test_polygon_contains_point():
    p = PolygonAreaOnScreen((
        Coordinate(0, 0), Coordinate(10, 0), Coordinate(10, 10), Coordinate(0, 10)
    ))
    assert (Coordinate(5, 5) in p) is True
    assert (Coordinate(15, 15) in p) is False

def test_rectangle_extended():
    r1 = RectangleAreaOnScreen(Coordinate(0, 0), Size(10, 10))
    r2 = RectangleAreaOnScreen(Coordinate(5, 5), Size(10, 10))
    # collide with rectangle
    assert r1.collide(r2) is True
    # collide with non-rectangle (polygon)
    p = PolygonAreaOnScreen((Coordinate(5, 5), Coordinate(15, 5), Coordinate(15, 15)))
    assert r1.collide(p) is True
    
    # contains point
    assert Coordinate(5, 5) in r1
    assert Coordinate(15, 15) not in r1
    
    # contains area
    assert r1 in RectangleAreaOnScreen(Coordinate(-1, -1), Size(20, 20))
    
    # pygame property
    assert r1.pygame == (Coordinate(0, 0), Size(10, 10))
    
    # add
    r3 = r1 + Coordinate(10, 10)
    assert r3.top_left == Coordinate(10, 10)
