from dataclasses import replace
from typing import Any, Protocol, Self

type Metadata = tuple[tuple[str, Any], ...]

METADATA_CACHE_KEY = ("metadata_cache_key", True)


class HasMetadata(Protocol):
    metadata: Metadata

    def add_metadata(self, **kwargs: Any) -> Self:
        meta = getattr(self, "metadata")
        metadata = meta + tuple(kwargs.items())
        return replace(self, metadata=metadata)
