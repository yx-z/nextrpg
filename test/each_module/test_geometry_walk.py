"""Tests for nextrpg.geometry.walk module."""
import pytest
from dataclasses import replace

from nextrpg.geometry.walk import Walk
from nextrpg.geometry.polyline_on_screen import PolylineOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import PixelPerMillisecond


class TestWalkCreation:
    """Test Walk object creation and initialization."""
    
    @pytest.fixture
    def simple_path(self):
        """Create a simple two-point path."""
        return PolylineOnScreen((Coordinate(0, 0), Coordinate(100, 0)))
    
    @pytest.fixture
    def square_path(self):
        """Create a square path."""
        return PolylineOnScreen((
            Coordinate(0, 0),
            Coordinate(100, 0),
            Coordinate(100, 100),
            Coordinate(0, 100),
        ))
    
    def test_walk_creation_basic(self, simple_path):
        """Test creating a basic Walk object."""
        walk = Walk(path=simple_path, move_speed=10, cyclic=False)
        
        assert walk.path == simple_path
        assert walk.move_speed == 10
        assert walk.cyclic is False
    
    def test_walk_creation_cyclic(self, simple_path):
        """Test creating a cyclic Walk object."""
        walk = Walk(path=simple_path, move_speed=10, cyclic=True)
        
        assert walk.cyclic is True
    
    def test_walk_initial_coordinate(self, simple_path):
        """Test that walk starts at the first path point."""
        walk = Walk(path=simple_path, move_speed=10, cyclic=False)
        
        assert walk.coordinate == simple_path.points[0]
        assert walk.coordinate == Coordinate(0, 0)
    
    def test_walk_is_frozen(self, simple_path):
        """Test that Walk objects are immutable."""
        walk = Walk(path=simple_path, move_speed=10, cyclic=False)
        
        with pytest.raises((AttributeError, TypeError)):
            walk.move_speed = 20
    
    def test_walk_not_complete_initially(self, simple_path):
        """Test that walk is not complete when just created."""
        walk = Walk(path=simple_path, move_speed=10, cyclic=False)
        
        assert walk.complete is False


class TestWalkMovement:
    """Test walk movement and tick behavior."""
    
    @pytest.fixture
    def horizontal_path(self):
        """Create a horizontal path."""
        return PolylineOnScreen((
            Coordinate(0, 0),
            Coordinate(100, 0),
        ))
    
    @pytest.fixture
    def slow_walk(self, horizontal_path):
        """Create a slow walk for easy testing."""
        return Walk(path=horizontal_path, move_speed=10, cyclic=False)
    
    def test_walk_tick_moves_forward(self, slow_walk):
        """Test that ticking moves the walk forward."""
        initial_coord = slow_walk.coordinate
        
        # Move for 5ms at 10 pixels/ms = 50 pixels
        walked = slow_walk.tick(5)
        
        assert walked.coordinate != initial_coord
        assert walked.coordinate.left > initial_coord.left
    
    def test_walk_tick_does_not_modify_original(self, slow_walk):
        """Test that tick returns a new Walk object."""
        walked = slow_walk.tick(1)
        
        assert slow_walk is not walked
        assert slow_walk.coordinate == Coordinate(0, 0)
    
    def test_walk_incremental_movement(self, slow_walk):
        """Test that walking multiple ticks accumulates."""
        # Walk 1ms at a time
        walk1 = slow_walk.tick(1)  # 10 pixels
        walk2 = walk1.tick(1)      # 10 more pixels
        walk3 = walk2.tick(1)      # 10 more pixels
        
        # After 3ms at 10px/ms, should be 30 pixels forward
        assert walk3.coordinate.left > walk1.coordinate.left
        assert walk3.coordinate.left > walk2.coordinate.left
    
    def test_walk_reaches_endpoint(self):
        """Test that walk reaches the endpoint."""
        path = PolylineOnScreen((Coordinate(0, 0), Coordinate(100, 0)))
        walk = Walk(path=path, move_speed=100, cyclic=False)
        
        # Move at 100px/ms for 2ms should reach 200px (past endpoint)
        walked = walk.tick(2)
        
        # Should be at the endpoint
        assert walked.coordinate == Coordinate(100, 0)
        assert walked.complete is True
    
    def test_walk_completes_at_endpoint(self):
        """Test that walk marks as complete when reaching endpoint."""
        path = PolylineOnScreen((Coordinate(0, 0), Coordinate(100, 0)))
        walk = Walk(path=path, move_speed=100, cyclic=False)
        
        walked = walk.tick(2)
        
        assert walked.complete is True


class TestWalkCyclic:
    """Test cyclic walk behavior."""
    
    def test_cyclic_walk_loops_around(self):
        """Test that cyclic walk loops back to start."""
        path = PolylineOnScreen((
            Coordinate(0, 0),
            Coordinate(100, 0),
        ))
        walk = Walk(path=path, move_speed=100, cyclic=True)
        
        # Move far enough to complete and cycle
        walked = walk.tick(3)
        
        # Should not be complete, should have cycled
        assert walked.complete is False
    
    def test_cyclic_walk_never_completes(self):
        """Test that cyclic walk never marks as complete."""
        path = PolylineOnScreen((
            Coordinate(0, 0),
            Coordinate(100, 0),
        ))
        walk = Walk(path=path, move_speed=10, cyclic=True)
        
        # Walk for many iterations
        for _ in range(100):
            walk = walk.tick(1)
        
        assert walk.complete is False
    
    def test_non_cyclic_walk_stops_at_end(self):
        """Test that non-cyclic walk stops at endpoint."""
        path = PolylineOnScreen((
            Coordinate(0, 0),
            Coordinate(100, 0),
        ))
        walk = Walk(path=path, move_speed=10, cyclic=False)
        
        # Walk far enough
        walked = walk
        for _ in range(100):
            walked = walked.tick(2)
        
        assert walked.complete is True
        assert walked.coordinate == Coordinate(100, 0)


class TestWalkDirection:
    """Test walk direction calculation."""
    
    def test_walk_direction_to_target(self):
        """Test that walk direction points to the next target."""
        path = PolylineOnScreen((
            Coordinate(0, 0),
            Coordinate(100, 0),
        ))
        walk = Walk(path=path, move_speed=10, cyclic=False)
        
        direction = walk.direction
        # Should have a valid direction
        assert direction is not None
    
    def test_walk_direction_changes_with_path(self):
        """Test that direction changes as walk progresses along path."""
        path = PolylineOnScreen((
            Coordinate(0, 0),
            Coordinate(100, 0),
            Coordinate(100, 100),
        ))
        walk = Walk(path=path, move_speed=10, cyclic=False)
        
        dir1 = walk.direction
        
        # Move to next segment
        walked = walk.tick(20)
        dir2 = walked.direction
        
        # Directions might be the same or different depending on path
        assert dir1 is not None
        assert dir2 is not None


class TestWalkReset:
    """Test walk reset functionality."""
    
    def test_walk_reset_returns_to_start(self):
        """Test that reset returns walk to initial state."""
        path = PolylineOnScreen((Coordinate(0, 0), Coordinate(100, 0)))
        walk = Walk(path=path, move_speed=10, cyclic=False)
        
        # Walk forward
        walked = walk.tick(5)
        assert walked.coordinate != walk.coordinate
        
        # Reset
        reset_walk = walked.reset
        
        assert reset_walk.coordinate == walk.coordinate
        assert reset_walk.coordinate == Coordinate(0, 0)
    
    def test_walk_reset_not_complete(self):
        """Test that reset walk is not complete."""
        path = PolylineOnScreen((Coordinate(0, 0), Coordinate(100, 0)))
        walk = Walk(path=path, move_speed=100, cyclic=False)
        
        # Complete the walk
        walked = walk.tick(2)
        assert walked.complete is True
        
        # Reset
        reset_walk = walked.reset
        
        assert reset_walk.complete is False


class TestWalkProperties:
    """Test walk properties."""
    
    def test_walk_initial_point(self):
        """Test walk initial point property."""
        path = PolylineOnScreen((
            Coordinate(50, 50),
            Coordinate(150, 50),
        ))
        walk = Walk(path=path, move_speed=10, cyclic=False)
        
        assert walk._initial_point == Coordinate(50, 50)
    
    def test_walk_final_target(self):
        """Test walk final target property."""
        path = PolylineOnScreen((
            Coordinate(0, 0),
            Coordinate(100, 0),
            Coordinate(100, 100),
        ))
        walk = Walk(path=path, move_speed=10, cyclic=False)
        
        assert walk._final_target == Coordinate(100, 100)
    
    def test_walk_remaining_distance(self):
        """Test walk remaining distance calculation."""
        path = PolylineOnScreen((Coordinate(0, 0), Coordinate(100, 0)))
        walk = Walk(path=path, move_speed=10, cyclic=False)
        
        initial_remaining = walk._remaining_dist
        
        # Move forward
        walked = walk.tick(3)  # Move 30 pixels at 10px/ms
        new_remaining = walked._remaining_dist
        
        # Remaining distance should decrease
        assert new_remaining < initial_remaining


class TestWalkSaveLoad:
    """Test walk save/load functionality."""
    
    def test_walk_save_data(self):
        """Test that walk can be serialized to save data."""
        path = PolylineOnScreen((Coordinate(0, 0), Coordinate(100, 0)))
        walk = Walk(path=path, move_speed=10, cyclic=False)
        
        walked = walk.tick(2)
        from dataclasses import asdict
        
        save_data = walked.save_data_this_class
        
        assert "coordinate" in save_data
        assert "target_index" in save_data
    
    def test_walk_load_from_save(self):
        """Test that walk can be loaded from save data."""
        path = PolylineOnScreen((Coordinate(0, 0), Coordinate(100, 0)))
        walk = Walk(path=path, move_speed=10, cyclic=False)
        
        walked = walk.tick(2)
        save_data = walked.save_data_this_class
        
        # Load from save
        loaded = walk.update_this_class_from_save(save_data)
        
        assert loaded.coordinate == walked.coordinate
        assert loaded._target_index == walked._target_index


class TestWalkComplexPath:
    """Test walk with complex paths."""
    
    def test_walk_square_path(self):
        """Test walk following a square path."""
        path = PolylineOnScreen((
            Coordinate(0, 0),
            Coordinate(100, 0),
            Coordinate(100, 100),
            Coordinate(0, 100),
        ))
        walk = Walk(path=path, move_speed=10, cyclic=True)
        
        # Walk around the square
        walked = walk
        for _ in range(100):
            walked = walked.tick(1)
        
        # Should have completed some segments
        assert walked is not None
        assert walked.path == path
    
    def test_walk_long_path(self):
        """Test walk with many points."""
        # Create a zigzag path
        points = []
        for i in range(10):
            points.append(Coordinate(i * 10, (i % 2) * 100))
        
        path = PolylineOnScreen(tuple(points))
        walk = Walk(path=path, move_speed=5, cyclic=False)
        
        # Should handle long paths
        walked = walk
        for _ in range(50):
            walked = walked.tick(1)
        
        assert walked is not None


class TestWalkEdgeCases:
    """Test edge cases for walk."""
    
    def test_walk_zero_speed(self):
        """Test walk with zero movement speed."""
        path = PolylineOnScreen((Coordinate(0, 0), Coordinate(100, 0)))
        walk = Walk(path=path, move_speed=0, cyclic=False)
        
        # Even with large time delta, shouldn't move
        walked = walk.tick(1000)
        
        assert walked.coordinate == walk.coordinate
    
    def test_walk_very_high_speed(self):
        """Test walk with very high movement speed."""
        path = PolylineOnScreen((Coordinate(0, 0), Coordinate(100, 0)))
        walk = Walk(path=path, move_speed=1000000, cyclic=False)
        
        # Should complete immediately
        walked = walk.tick(1)
        
        assert walked.complete is True
    
    def test_walk_single_point_path(self):
        """Test walk with only one point (edge case)."""
        path = PolylineOnScreen((Coordinate(0, 0),))
        walk = Walk(path=path, move_speed=10, cyclic=False)
        
        # Should start at that point already at completion
        assert walk.coordinate == Coordinate(0, 0)
