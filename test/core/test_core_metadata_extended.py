"""Extended tests for nextrpg.core.metadata module."""
import pytest
from dataclasses import dataclass
from nextrpg.core.metadata import HasMetadata, Metadata, METADATA_CACHE_KEY


class TestMetadataType:
    """Tests for Metadata type alias."""

    def test_metadata_is_tuple_of_tuples(self):
        """Test Metadata is a tuple of (str, Any) pairs."""
        metadata: Metadata = (("key1", "value1"), ("key2", 42))
        assert isinstance(metadata, tuple)
        assert metadata[0] == ("key1", "value1")
        assert metadata[1] == ("key2", 42)

    def test_empty_metadata(self):
        """Test empty Metadata."""
        metadata: Metadata = ()
        assert len(metadata) == 0


class TestMetadataCacheKey:
    """Tests for METADATA_CACHE_KEY constant."""

    def test_metadata_cache_key_is_tuple(self):
        """Test METADATA_CACHE_KEY is a tuple."""
        assert isinstance(METADATA_CACHE_KEY, tuple)

    def test_metadata_cache_key_value(self):
        """Test METADATA_CACHE_KEY has expected value."""
        assert METADATA_CACHE_KEY == ("metadata_cache_key", True)


class TestHasMetadata:
    """Tests for HasMetadata protocol."""

    def test_has_metadata_protocol_exists(self):
        """Test HasMetadata protocol is importable."""
        assert HasMetadata is not None

    def test_has_metadata_has_add_metadata(self):
        """Test HasMetadata has add_metadata method."""
        assert hasattr(HasMetadata, "add_metadata")

    def test_add_metadata_via_dataclass(self):
        """Test add_metadata on a concrete dataclass implementation."""
        @dataclass(frozen=True)
        class MyObj:
            metadata: Metadata = ()
            
            def add_metadata(self, **kwargs):
                from nextrpg.core.metadata import HasMetadata
                return HasMetadata.add_metadata(self, **kwargs)

        obj = MyObj()
        updated = obj.add_metadata(level=5, name="hero")
        assert ("level", 5) in updated.metadata
        assert ("name", "hero") in updated.metadata

    def test_add_metadata_preserves_existing(self):
        """Test add_metadata preserves existing metadata."""
        @dataclass(frozen=True)
        class MyObj:
            metadata: Metadata = ()
            
            def add_metadata(self, **kwargs):
                from nextrpg.core.metadata import HasMetadata
                return HasMetadata.add_metadata(self, **kwargs)

        obj = MyObj(metadata=(("existing", "data"),))
        updated = obj.add_metadata(new_key="new_value")
        assert ("existing", "data") in updated.metadata
        assert ("new_key", "new_value") in updated.metadata
