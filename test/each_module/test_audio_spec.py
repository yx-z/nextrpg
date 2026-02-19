"""
Tests for nextrpg.audio module (sound_spec and music_spec).
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from nextrpg.audio.music_spec import MusicSpec
from nextrpg.audio.sound_spec import SoundSpec
from nextrpg.config.system.audio_config import AudioConfig


class TestAudioConfig:
    """Tests for AudioConfig class."""

    def test_audio_config_creation_defaults(self):
        """Test creating AudioConfig with defaults."""
        config = AudioConfig()
        assert config.volume == 1.0
        assert config.fade_in_duration == 0
        assert config.fade_out_duration == 0

    def test_audio_config_creation_custom(self):
        """Test creating AudioConfig with custom values."""
        config = AudioConfig(
            volume=0.5, fade_in_duration=500, fade_out_duration=1000
        )
        assert config.volume == 0.5
        assert config.fade_in_duration == 500
        assert config.fade_out_duration == 1000

    def test_audio_config_with_volume(self):
        """Test with_volume method."""
        config = AudioConfig()
        new_config = config.with_volume(0.7)

        assert config.volume == 1.0  # Original unchanged
        assert new_config.volume == 0.7
        assert new_config.fade_in_duration == 0

    def test_audio_config_with_fade_in(self):
        """Test with_fade_in method."""
        config = AudioConfig()
        new_config = config.with_fade_in(500)

        assert config.fade_in_duration == 0  # Original unchanged
        assert new_config.fade_in_duration == 500
        assert new_config.volume == 1.0

    def test_audio_config_with_fade_out(self):
        """Test with_fade_out method."""
        config = AudioConfig()
        new_config = config.with_fade_out(1000)

        assert config.fade_out_duration == 0  # Original unchanged
        assert new_config.fade_out_duration == 1000
        assert new_config.volume == 1.0

    def test_audio_config_chaining(self):
        """Test chaining config methods."""
        config = AudioConfig()
        new_config = (
            config.with_volume(0.8).with_fade_in(200).with_fade_out(300)
        )

        assert new_config.volume == 0.8
        assert new_config.fade_in_duration == 200
        assert new_config.fade_out_duration == 300


class TestSoundSpec:
    """Tests for SoundSpec class."""

    def test_sound_spec_creation_minimal(self):
        """Test creating SoundSpec with minimal config."""
        config = AudioConfig(volume=0.8)
        spec = SoundSpec(file="sound.wav", loop=False, config=config)

        assert spec.file == "sound.wav"
        assert spec.loop is False
        assert spec.config == config

    def test_sound_spec_loop_flag_no_loop(self):
        """Test loop_flag when loop is False."""
        config = AudioConfig()
        spec = SoundSpec(file="sound.wav", loop=False, config=config)

        assert spec.loop_flag == 0

    def test_sound_spec_loop_flag_loop(self):
        """Test loop_flag when loop is True."""
        config = AudioConfig()
        spec = SoundSpec(file="sound.wav", loop=True, config=config)

        assert spec.loop_flag == -1

    def test_sound_spec_with_path_object(self):
        """Test SoundSpec with Path object."""
        config = AudioConfig()
        path = Path("audio/sound.wav")
        spec = SoundSpec(file=path, loop=False, config=config)

        assert spec.file == path

    def test_sound_spec_equality(self):
        """Test SoundSpec equality."""
        config = AudioConfig(volume=0.8)
        spec1 = SoundSpec(file="sound.wav", loop=False, config=config)
        spec2 = SoundSpec(file="sound.wav", loop=False, config=config)

        assert spec1 == spec2

    def test_sound_spec_inequality_different_file(self):
        """Test SoundSpec inequality with different files."""
        config = AudioConfig()
        spec1 = SoundSpec(file="sound1.wav", loop=False, config=config)
        spec2 = SoundSpec(file="sound2.wav", loop=False, config=config)

        assert spec1 != spec2

    def test_sound_spec_inequality_different_loop(self):
        """Test SoundSpec inequality with different loop."""
        config = AudioConfig()
        spec1 = SoundSpec(file="sound.wav", loop=False, config=config)
        spec2 = SoundSpec(file="sound.wav", loop=True, config=config)

        assert spec1 != spec2

    def test_sound_spec_inequality_different_config(self):
        """Test SoundSpec inequality with different config."""
        config1 = AudioConfig(volume=0.8)
        config2 = AudioConfig(volume=0.5)
        spec1 = SoundSpec(file="sound.wav", loop=False, config=config1)
        spec2 = SoundSpec(file="sound.wav", loop=False, config=config2)

        assert spec1 != spec2

    def test_sound_spec_hashable(self):
        """Test SoundSpec is hashable."""
        config = AudioConfig()
        spec1 = SoundSpec(file="sound.wav", loop=False, config=config)
        spec2 = SoundSpec(file="sound.wav", loop=False, config=config)

        # Should be able to use in sets
        sound_set = {spec1, spec2}
        assert len(sound_set) == 1  # They're equal, so only one in set

    def test_sound_spec_frozen(self):
        """Test SoundSpec is frozen."""
        config = AudioConfig()
        spec = SoundSpec(file="sound.wav", loop=False, config=config)

        with pytest.raises(Exception):  # FrozenInstanceError
            spec.file = "other.wav"


class TestMusicSpec:
    """Tests for MusicSpec class."""

    def test_music_spec_creation_defaults(self):
        """Test creating MusicSpec with defaults."""
        # When creating MusicSpec without config, it uses default factory
        # which calls config().system.music
        mock_music_config = AudioConfig(volume=0.9)
        spec = MusicSpec(file="music.ogg", config=mock_music_config)

        assert spec.file == "music.ogg"
        assert spec.loop is True  # Music loops by default
        assert spec.config.volume == 0.9

    def test_music_spec_custom_config(self):
        """Test creating MusicSpec with custom config."""
        config = AudioConfig(volume=0.7, fade_in_duration=500)
        spec = MusicSpec(file="music.ogg", config=config)

        assert spec.file == "music.ogg"
        assert spec.loop is True
        assert spec.config == config

    def test_music_spec_custom_loop(self):
        """Test creating MusicSpec with custom loop value."""
        config = AudioConfig()
        spec = MusicSpec(file="music.ogg", loop=False, config=config)

        assert spec.file == "music.ogg"
        assert spec.loop is False
        assert spec.config == config

    def test_music_spec_loop_flag_true(self):
        """Test MusicSpec loop_flag with loop=True."""
        config = AudioConfig()
        spec = MusicSpec(file="music.ogg", loop=True, config=config)

        assert spec.loop_flag == -1

    def test_music_spec_loop_flag_false(self):
        """Test MusicSpec loop_flag with loop=False."""
        config = AudioConfig()
        spec = MusicSpec(file="music.ogg", loop=False, config=config)

        assert spec.loop_flag == 0

    def test_music_spec_with_path(self):
        """Test MusicSpec with Path object."""
        config = AudioConfig()
        path = Path("audio/music.ogg")
        spec = MusicSpec(file=path, config=config)

        assert spec.file == path

    def test_music_spec_equality(self):
        """Test MusicSpec equality."""
        config = AudioConfig(volume=0.9)
        spec1 = MusicSpec(file="music.ogg", config=config)
        spec2 = MusicSpec(file="music.ogg", config=config)

        assert spec1 == spec2

    def test_music_spec_inherits_from_audio_spec(self):
        """Test MusicSpec inherits from AudioSpec methods."""
        config = AudioConfig()
        spec = MusicSpec(file="music.ogg", config=config)

        # Should have _tuple property from AudioSpec
        assert hasattr(spec, "_tuple")
        assert isinstance(spec._tuple, tuple)

    def test_music_spec_hashable(self):
        """Test MusicSpec is hashable."""
        config = AudioConfig()
        spec1 = MusicSpec(file="music.ogg", config=config)
        spec2 = MusicSpec(file="music.ogg", config=config)

        music_set = {spec1, spec2}
        assert len(music_set) == 1


class TestSoundAndMusicComparison:
    """Tests comparing SoundSpec and MusicSpec."""

    def test_sound_vs_music_same_file(self):
        """Test SoundSpec and MusicSpec with same file are different."""
        config = AudioConfig()
        sound = SoundSpec(file="audio.wav", loop=True, config=config)
        music = MusicSpec(file="audio.wav", loop=True, config=config)

        # They should be different types
        assert isinstance(sound, SoundSpec)
        assert isinstance(music, MusicSpec)
        # But not equal because they're different types
        # (equality is based on _tuple which includes type)

    def test_audio_config_application(self):
        """Test that AudioConfig methods work on both SoundSpec and MusicSpec."""
        config = AudioConfig().with_volume(0.5)

        sound = SoundSpec(file="sound.wav", loop=False, config=config)
        music = MusicSpec(file="music.ogg", config=config)

        assert sound.config.volume == 0.5
        assert music.config.volume == 0.5


class TestAudioSpecEdgeCases:
    """Tests for edge cases in audio specs."""

    def test_audio_config_volume_zero(self):
        """Test AudioConfig with zero volume."""
        config = AudioConfig(volume=0.0)
        assert config.volume == 0.0

    def test_audio_config_volume_max(self):
        """Test AudioConfig with maximum volume."""
        config = AudioConfig(volume=2.0)
        assert config.volume == 2.0

    def test_audio_config_large_duration(self):
        """Test AudioConfig with large durations."""
        config = AudioConfig(fade_in_duration=60000, fade_out_duration=60000)
        assert config.fade_in_duration == 60000
        assert config.fade_out_duration == 60000

    def test_sound_spec_path_as_string(self):
        """Test SoundSpec accepts both string and Path."""
        config = AudioConfig()

        sound_str = SoundSpec(file="sound.wav", loop=False, config=config)
        sound_path = SoundSpec(
            file=Path("sound.wav"), loop=False, config=config
        )

        assert sound_str.file == "sound.wav"
        assert sound_path.file == Path("sound.wav")
