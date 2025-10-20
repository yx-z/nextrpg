from dataclasses import is_dataclass, replace
from typing import Any, Protocol, Self


class HasMetadata(Protocol):
    def add_metadata(self, **kwargs: Any) -> Self:
        assert is_dataclass(
            self
        ), f"Can only add metadata to dataclasses. Got {self}."
        assert isinstance(
            meta := getattr(self, "metadata", None), dict
        ), f"Need self.metadata dict. Got {self}."
        metadata = meta | kwargs
        return replace(self, metadata=metadata)
