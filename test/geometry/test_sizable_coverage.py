import pytest
from dataclasses import dataclass
from nextrpg.geometry.sizable import Sizable
from nextrpg.geometry.size import Size
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.anchor import Anchor

@dataclass
class DummySizable:
    top_left: Coordinate
    size: Size
    
    # We need to mix in the properties from Sizable manually since it's a Protocol
    # or just use the protocol methods directly if they were implemented in a Mixin.
    # In nextrpg, Sizable is a Protocol but has concrete methods. 
    # Python's Protocol doesn't allow calling its methods on instances of classes that 
    # don't inherit from it unless we do some trickery or the class actually inherits.
    
class RealSizable(Sizable):
    def __init__(self, top_left, size):
        self.top_left = top_left
        self.size = size

def test_sizable_all_properties():
    s = RealSizable(Coordinate(10, 20), Size(100, 200))
    
    assert s.width.value == 100
    assert s.height.value == 200
    assert s.top.value == 20
    assert s.left.value == 10
    assert s.bottom.value == 220
    assert s.right.value == 110
    
    assert s.top_right == Coordinate(110, 20)
    assert s.bottom_left == Coordinate(10, 220)
    assert s.bottom_right == Coordinate(110, 220)
    assert s.top_center == Coordinate(60, 20)
    assert s.bottom_center == Coordinate(60, 220)
    assert s.center_left == Coordinate(10, 120)
    assert s.center_right == Coordinate(110, 120)
    assert s.center == Coordinate(60, 120)
    
    # Test at_anchor for all anchors
    assert s.at_anchor(Anchor.TOP_LEFT) == s.top_left
    assert s.at_anchor(Anchor.TOP_CENTER) == s.top_center
    assert s.at_anchor(Anchor.TOP_RIGHT) == s.top_right
    assert s.at_anchor(Anchor.CENTER_LEFT) == s.center_left
    assert s.at_anchor(Anchor.CENTER) == s.center
    assert s.at_anchor(Anchor.CENTER_RIGHT) == s.center_right
    assert s.at_anchor(Anchor.BOTTOM_LEFT) == s.bottom_left
    assert s.at_anchor(Anchor.BOTTOM_CENTER) == s.bottom_center
    assert s.at_anchor(Anchor.BOTTOM_RIGHT) == s.bottom_right
    
    # Test rectangle_area_on_screen
    area = s.rectangle_area_on_screen
    assert area.top_left == s.top_left
    assert area.size == s.size
