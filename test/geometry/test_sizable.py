import pytest
from nextrpg.geometry.sizable import Sizable
from nextrpg.geometry.size import Size, Width, Height
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.anchor import Anchor

def test_sizable_protocol():
    """Test Sizable protocol structure."""
    # Since Sizable is a Protocol, its attributes are defined in __annotations__
    assert "size" in Sizable.__annotations__
    assert "top_left" in Sizable.__annotations__
    
    # And its methods are part of the class dict
    assert "width" in Sizable.__dict__
    assert "height" in Sizable.__dict__
    assert "top" in Sizable.__dict__
    assert "left" in Sizable.__dict__
    assert "bottom" in Sizable.__dict__
    assert "right" in Sizable.__dict__
    assert "at_anchor" in Sizable.__dict__
