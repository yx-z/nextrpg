"""Tests for nextrpg sub-config modules."""
import pytest
from nextrpg.config.animation_config import AnimationConfig
from nextrpg.config.map_config import MapConfig
from nextrpg.config.debug_config import DebugConfig
from nextrpg.drawing.color import Color


class TestAnimationConfig:
    """Tests for AnimationConfig."""

    def test_default_duration(self):
        """Test default animation duration is 400ms."""
        cfg = AnimationConfig()
        assert cfg.default_timed_animation_duration == 400

    def test_custom_duration(self):
        """Test custom animation duration."""
        cfg = AnimationConfig(default_timed_animation_duration=800)
        assert cfg.default_timed_animation_duration == 800

    def test_animation_config_is_frozen(self):
        """Test AnimationConfig is immutable."""
        cfg = AnimationConfig()
        with pytest.raises(Exception):
            cfg.default_timed_animation_duration = 1000


class TestMapConfig:
    """Tests for MapConfig."""

    def test_default_layer_names(self):
        """Test default layer names."""
        cfg = MapConfig()
        assert cfg.background == "background"
        assert cfg.foreground == "foreground"
        assert cfg.above_character == "above_character"
        assert cfg.collision == "collision"

    def test_custom_layer_names(self):
        """Test custom layer names."""
        cfg = MapConfig(
            background="bg",
            foreground="fg",
            above_character="above",
            collision="col",
        )
        assert cfg.background == "bg"
        assert cfg.foreground == "fg"
        assert cfg.above_character == "above"
        assert cfg.collision == "col"

    def test_map_config_is_frozen(self):
        """Test MapConfig is immutable."""
        cfg = MapConfig()
        with pytest.raises(Exception):
            cfg.background = "other"


class TestDebugConfig:
    """Tests for DebugConfig."""

    def test_default_player_collide(self):
        """Test default player_collide_with_others is True."""
        cfg = DebugConfig()
        assert cfg.player_collide_with_others is True

    def test_custom_player_collide(self):
        """Test custom player_collide_with_others."""
        cfg = DebugConfig(player_collide_with_others=False)
        assert cfg.player_collide_with_others is False

    def test_default_drawing_background_color(self):
        """Test default drawing_background has a color."""
        cfg = DebugConfig()
        assert cfg.drawing_background is not None
        assert isinstance(cfg.drawing_background, Color)

    def test_debug_config_is_frozen(self):
        """Test DebugConfig is immutable."""
        cfg = DebugConfig()
        with pytest.raises(Exception):
            cfg.player_collide_with_others = False

    def test_debug_config_none_colors(self):
        """Test DebugConfig with None colors."""
        cfg = DebugConfig(
            drawing_background=None,
            collision_rectangle=None,
        )
        assert cfg.drawing_background is None
        assert cfg.collision_rectangle is None
