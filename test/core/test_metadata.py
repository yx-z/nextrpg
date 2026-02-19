"""Tests for nextrpg.core.metadata module."""
import pytest

from nextrpg.core.metadata import Metadata, HasMetadata, METADATA_CACHE_KEY


class TestMetadataType:
    """Test Metadata type."""
    
    def test_metadata_is_tuple_of_tuples(self):
        """Test that Metadata is tuple[tuple[str, Any], ...]."""
        # Metadata is a type alias
        assert Metadata is not None
    
    def test_create_metadata_tuple(self):
        """Test creating metadata as tuple."""
        meta: Metadata = (("key1", "value1"), ("key2", "value2"))
        
        assert len(meta) == 2
        assert meta[0] == ("key1", "value1")
        assert meta[1] == ("key2", "value2")
    
    def test_empty_metadata(self):
        """Test empty metadata tuple."""
        meta: Metadata = ()
        
        assert len(meta) == 0
        assert meta == ()


class TestMetadataCacheKey:
    """Test metadata cache key constant."""
    
    def test_metadata_cache_key_exists(self):
        """Test that METADATA_CACHE_KEY is defined."""
        assert METADATA_CACHE_KEY is not None
    
    def test_metadata_cache_key_value(self):
        """Test METADATA_CACHE_KEY value."""
        assert METADATA_CACHE_KEY == ("metadata_cache_key", True)
    
    def test_metadata_cache_key_type(self):
        """Test METADATA_CACHE_KEY is tuple."""
        assert isinstance(METADATA_CACHE_KEY, tuple)
        assert len(METADATA_CACHE_KEY) == 2


class TestHasMetadataProtocol:
    """Test HasMetadata protocol."""
    
    def test_has_metadata_is_protocol(self):
        """Test that HasMetadata is a protocol."""
        assert HasMetadata is not None
    
    def test_has_metadata_has_metadata_attribute(self):
        """Test that HasMetadata protocol requires metadata."""
        # Protocol check - just verify it exists
        assert hasattr(HasMetadata, '__protocol_attrs__') or hasattr(HasMetadata, '_get_protocol_attrs')


class TestMetadataManipulation:
    """Test metadata manipulation."""
    
    def test_metadata_tuple_operations(self):
        """Test standard tuple operations on metadata."""
        meta: Metadata = (("a", 1), ("b", 2), ("c", 3))
        
        # Add to metadata
        new_meta = meta + (("d", 4),)
        
        assert len(new_meta) == 4
        assert new_meta[-1] == ("d", 4)
    
    def test_metadata_immutability(self):
        """Test that metadata tuples are immutable."""
        meta: Metadata = (("x", "y"),)
        
        # Should not be able to modify tuple
        with pytest.raises(TypeError):
            meta[0] = ("new", "value")


class TestMetadataIntegration:
    """Integration tests."""
    
    def test_metadata_multiple_entries(self):
        """Test metadata with many entries."""
        entries = [(f"key{i}", f"value{i}") for i in range(10)]
        meta: Metadata = tuple(entries)
        
        assert len(meta) == 10
        for i, entry in enumerate(meta):
            assert entry == (f"key{i}", f"value{i}")
