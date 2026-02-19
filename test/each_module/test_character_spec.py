"""
Tests for nextrpg.character module (character specs).
"""

import pytest
from unittest.mock import patch, MagicMock
from dataclasses import replace
from nextrpg.character.character_spec import CharacterSpec
from nextrpg.character.player_spec import PlayerSpec
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.config.character.behavior_config import BehaviorConfig
from nextrpg.geometry.scaling import HeightScaling, WidthScaling


class TestBehaviorConfig:
    """Tests for BehaviorConfig class."""
    
    def test_behavior_config_defaults(self):
        """Test BehaviorConfig with defaults."""
        config = BehaviorConfig()
        
        assert config.move_speed == 0.2
        assert isinstance(config.bounding_rectangle_scaling, HeightScaling)
        assert config.bounding_rectangle_scaling.value == 0.4
        assert isinstance(config.start_event_scaling, WidthScaling)
        assert config.start_event_scaling.value == 1.2
    
    def test_behavior_config_custom(self):
        """Test BehaviorConfig with custom values."""
        behavior = BehaviorConfig(
            move_speed=0.5,
            bounding_rectangle_scaling=HeightScaling(0.6),
            start_event_scaling=WidthScaling(1.5)
        )
        
        assert behavior.move_speed == 0.5
        assert behavior.bounding_rectangle_scaling.value == 0.6
        assert behavior.start_event_scaling.value == 1.5
    
    def test_behavior_config_frozen(self):
        """Test BehaviorConfig is frozen."""
        config = BehaviorConfig()
        
        with pytest.raises(Exception):  # FrozenInstanceError
            config.move_speed = 0.3


class TestCharacterSpec:
    """Tests for CharacterSpec class."""
    
    def test_character_spec_creation(self):
        """Test creating a CharacterSpec."""
        with patch('nextrpg.config.config.config') as mock_config:
            mock_behavior = BehaviorConfig()
            mock_config.return_value.character.behavior = mock_behavior
            
            drawing = MagicMock()
            spec = CharacterSpec(
                unique_name="hero",
                character_drawing=drawing
            )
            
            assert spec.unique_name == "hero"
            assert spec.character_drawing is drawing
            assert spec.collide_with_others is True
            assert spec.avatar is None
            assert spec.display_name == "hero"
    
    def test_character_spec_custom_display_name(self):
        """Test CharacterSpec with custom display name."""
        with patch('nextrpg.config.config.config') as mock_config:
            mock_behavior = BehaviorConfig()
            mock_config.return_value.character.behavior = mock_behavior
            
            drawing = MagicMock()
            spec = CharacterSpec(
                unique_name="hero",
                display_name="The Hero",
                character_drawing=drawing
            )
            
            assert spec.unique_name == "hero"
            assert spec.display_name == "The Hero"
    
    def test_character_spec_no_collision(self):
        """Test CharacterSpec with collision disabled."""
        with patch('nextrpg.config.config.config') as mock_config:
            mock_behavior = BehaviorConfig()
            mock_config.return_value.character.behavior = mock_behavior
            
            drawing = MagicMock()
            spec = CharacterSpec(
                unique_name="ghost",
                collide_with_others=False,
                character_drawing=drawing
            )
            
            assert spec.collide_with_others is False
    
    def test_character_spec_with_avatar(self):
        """Test CharacterSpec with avatar."""
        with patch('nextrpg.config.config.config') as mock_config:
            mock_behavior = BehaviorConfig()
            mock_config.return_value.character.behavior = mock_behavior
            
            drawing = MagicMock()
            avatar = MagicMock()
            spec = CharacterSpec(
                unique_name="hero",
                avatar=avatar,
                character_drawing=drawing
            )
            
            assert spec.avatar is avatar
    
    def test_character_spec_custom_config(self):
        """Test CharacterSpec with custom config."""
        behavior = BehaviorConfig(move_speed=0.3)
        drawing = MagicMock()
        
        spec = CharacterSpec(
            unique_name="hero",
            character_drawing=drawing,
            config=behavior
        )
        
        assert spec.config.move_speed == 0.3
    
    def test_character_spec_save_data(self):
        """Test CharacterSpec save_data property."""
        with patch('nextrpg.config.config.config') as mock_config:
            mock_behavior = BehaviorConfig()
            mock_config.return_value.character.behavior = mock_behavior
            
            drawing = MagicMock()
            spec = CharacterSpec(
                unique_name="hero",
                character_drawing=drawing
            )
            
            assert spec.save_data_this_class() == "hero"
    
    def test_character_spec_update_from_save(self):
        """Test CharacterSpec update from save data."""
        with patch('nextrpg.config.config.config') as mock_config:
            mock_behavior = BehaviorConfig()
            mock_config.return_value.character.behavior = mock_behavior
            
            drawing = MagicMock()
            spec = CharacterSpec(
                unique_name="hero",
                character_drawing=drawing
            )
            
            updated = spec.update_this_class_from_save("villain")
            assert updated.unique_name == "villain"
    
    def test_character_spec_frozen(self):
        """Test CharacterSpec is frozen."""
        with patch('nextrpg.config.config.config') as mock_config:
            mock_behavior = BehaviorConfig()
            mock_config.return_value.character.behavior = mock_behavior
            
            drawing = MagicMock()
            spec = CharacterSpec(
                unique_name="hero",
                character_drawing=drawing
            )
            
            with pytest.raises(Exception):  # FrozenInstanceError
                spec.unique_name = "villain"


class TestPlayerSpec:
    """Tests for PlayerSpec class."""
    
    def test_player_spec_creation(self):
        """Test creating a PlayerSpec."""
        with patch('nextrpg.config.config.config') as mock_config:
            mock_behavior = BehaviorConfig()
            mock_config.return_value.character.behavior = mock_behavior
            
            drawing = MagicMock()
            spec = PlayerSpec(
                unique_name="player",
                character_drawing=drawing
            )
            
            assert spec.unique_name == "player"
            assert spec.character_drawing is drawing
            assert spec.coordinate_override is None
    
    def test_player_spec_with_coordinate_override(self):
        """Test PlayerSpec with coordinate override."""
        with patch('nextrpg.config.config.config') as mock_config:
            mock_behavior = BehaviorConfig()
            mock_config.return_value.character.behavior = mock_behavior
            
            drawing = MagicMock()
            coord = Coordinate(100, 200)
            spec = PlayerSpec(
                unique_name="player",
                character_drawing=drawing,
                coordinate_override=coord
            )
            
            assert spec.coordinate_override == coord
    
    def test_player_spec_to_map(self):
        """Test PlayerSpec.to_map method."""
        with patch('nextrpg.config.config.config') as mock_config:
            mock_behavior = BehaviorConfig()
            mock_config.return_value.character.behavior = mock_behavior
            
            drawing1 = MagicMock()
            drawing2 = MagicMock()
            coord = Coordinate(100, 200)
            
            player = PlayerSpec(
                unique_name="player",
                character_drawing=drawing1,
                coordinate_override=coord
            )
            
            mapped = player.to_map("hero", drawing2)
            
            assert mapped.unique_name == "hero"
            assert mapped.character_drawing is drawing2
            assert mapped.coordinate_override is None
    
    def test_player_spec_to_map_preserves_other_fields(self):
        """Test PlayerSpec.to_map preserves other fields."""
        with patch('nextrpg.config.config.config') as mock_config:
            mock_behavior = BehaviorConfig(move_speed=0.3)
            mock_config.return_value.character.behavior = mock_behavior
            
            drawing1 = MagicMock()
            drawing2 = MagicMock()
            avatar = MagicMock()
            
            player = PlayerSpec(
                unique_name="player",
                character_drawing=drawing1,
                display_name="The Hero",
                avatar=avatar,
                config=mock_behavior
            )
            
            mapped = player.to_map("hero", drawing2)
            
            assert mapped.display_name == "The Hero"
            assert mapped.avatar is avatar
            assert mapped.config is mock_behavior
    
    def test_player_spec_inherits_from_character_spec(self):
        """Test PlayerSpec inherits from CharacterSpec."""
        with patch('nextrpg.config.config.config') as mock_config:
            mock_behavior = BehaviorConfig()
            mock_config.return_value.character.behavior = mock_behavior
            
            drawing = MagicMock()
            player = PlayerSpec(
                unique_name="player",
                character_drawing=drawing
            )
            
            assert isinstance(player, CharacterSpec)
            assert player.collide_with_others is True
    
    def test_player_spec_frozen(self):
        """Test PlayerSpec is frozen."""
        with patch('nextrpg.config.config.config') as mock_config:
            mock_behavior = BehaviorConfig()
            mock_config.return_value.character.behavior = mock_behavior
            
            drawing = MagicMock()
            player = PlayerSpec(
                unique_name="player",
                character_drawing=drawing
            )
            
            with pytest.raises(Exception):  # FrozenInstanceError
                player.coordinate_override = Coordinate(0, 0)
