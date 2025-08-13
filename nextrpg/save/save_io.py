from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from nextrpg.global_config.global_config import config
from nextrpg.global_config.save_config import SaveConfig


@dataclass(frozen=True)
class SaveIo[T](ABC):
    config: SaveConfig = field(default_factory=lambda: config().save)

    @abstractmethod
    def save(self, slot: str, source: T) -> None: ...

    @abstractmethod
    def load(self, slot: str, source: T) -> T: ...
