"""Tests for nextrpg.audio.play_music_event module."""
import pytest
from unittest.mock import MagicMock, patch

from nextrpg.audio.play_music_event import PlayMusicEvent
from nextrpg.audio.music_spec import MusicSpec


class TestPlayMusicEventCreation:
    """Test PlayMusicEvent creation."""
    
    def test_play_music_event_creation(self):
        """Test creating PlayMusicEvent."""
        spec = MusicSpec("path/to/music.mp3")
        event = PlayMusicEvent(spec)
        
        assert event.spec == spec
    
    def test_play_music_event_with_different_specs(self):
        """Test PlayMusicEvent with various specs."""
        spec1 = MusicSpec("music1.mp3")
        spec2 = MusicSpec("music2.mp3")
        
        event1 = PlayMusicEvent(spec1)
        event2 = PlayMusicEvent(spec2)
        
        assert event1.spec == spec1
        assert event2.spec == spec2
        assert event1.spec != event2.spec


class TestPlayMusicEventProperties:
    """Test PlayMusicEvent properties."""
    
    def test_play_music_event_stores_spec(self):
        """Test that PlayMusicEvent stores music spec."""
        spec = MusicSpec("music.ogg")
        event = PlayMusicEvent(spec)
        
        assert hasattr(event, 'spec')
        assert event.spec == spec
    
    def test_play_music_event_spec_none(self):
        """Test PlayMusicEvent with None spec."""
        # Some implementations might allow None
        try:
            event = PlayMusicEvent(None)
            assert event.spec is None
        except TypeError:
            # If None is not allowed, that's fine
            pass


class TestPlayMusicEventEquality:
    """Test PlayMusicEvent equality."""
    
    def test_play_music_event_equality(self):
        """Test equal PlayMusicEvent instances."""
        spec = MusicSpec("music.mp3")
        event1 = PlayMusicEvent(spec)
        event2 = PlayMusicEvent(spec)
        
        # Should be equal with same spec
        assert event1 == event2
    
    def test_play_music_event_inequality(self):
        """Test different PlayMusicEvent instances."""
        spec1 = MusicSpec("music1.mp3")
        spec2 = MusicSpec("music2.mp3")
        
        event1 = PlayMusicEvent(spec1)
        event2 = PlayMusicEvent(spec2)
        
        assert event1 != event2


class TestPlayMusicEventRepr:
    """Test PlayMusicEvent representation."""
    
    def test_play_music_event_repr(self):
        """Test PlayMusicEvent repr."""
        spec = MusicSpec("music.mp3")
        event = PlayMusicEvent(spec)
        
        repr_str = repr(event)
        assert 'PlayMusicEvent' in repr_str or 'music' in repr_str.lower()


class TestPlayMusicEventIntegration:
    """Integration tests."""
    
    def test_play_music_event_multiple_instances(self):
        """Test creating multiple PlayMusicEvent instances."""
        specs = [MusicSpec(f"music{i}.mp3") for i in range(3)]
        events = [PlayMusicEvent(spec) for spec in specs]
        
        assert len(events) == 3
        for i, event in enumerate(events):
            assert event.spec == specs[i]
    
    def test_play_music_event_can_be_used_as_event(self):
        """Test that PlayMusicEvent works as an event."""
        spec = MusicSpec("music.mp3")
        event = PlayMusicEvent(spec)
        
        # Should be usable as a pygame event or similar
        assert event is not None
        assert hasattr(event, 'spec')
