from dataclasses import is_dataclass, replace
from typing import Any, Protocol, Self

type Metadata = tuple[tuple[str, Any], ...]

METADATA_AS_CACHE_KEY = ("metadata_as_cache_key", True)


class HasMetadata(Protocol):
    metadata: Metadata

    def add_metadata(self, **kwargs: Any) -> Self:
        assert is_dataclass(
            self
        ), f"Can only add metadata to dataclasses. Got {self}."
        meta = getattr(self, "metadata", None)
        assert isinstance(
            meta, tuple
        ), f"Need self.metadata tuple[tuple[str, Any]]. Got {self}."
        metadata = meta + tuple(kwargs.items())
        return replace(self, metadata=metadata)
