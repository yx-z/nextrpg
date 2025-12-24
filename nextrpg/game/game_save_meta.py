from dataclasses import KW_ONLY, dataclass, field
from datetime import datetime
from functools import cached_property
from typing import Any, Self, override

from nextrpg import __version__
from nextrpg.config.config import config
from nextrpg.config.system.save_config import SaveConfig
from nextrpg.core.dataclass_with_default import private_init_below
from nextrpg.core.save import LoadFromSave


@dataclass(frozen=True)
class GameSaveMeta(LoadFromSave):
    slot: str
    config: SaveConfig = field(default_factory=lambda: config().system.save)
    _: KW_ONLY = private_init_below()
    save_time: datetime = field(default_factory=datetime.now)
    nextrpg_version: str = __version__

    def save_key(self) -> str:
        return self.slot

    @cached_property
    def save_time_str(self) -> str:
        return self.save_time.strftime(self.config.time_format)

    @override
    @cached_property
    def save_data_this_class(self) -> dict[str, Any]:
        return {
            "slot": self.slot,
            "save_time": self.save_time_str,
            "nextrpg_version": self.nextrpg_version,
        }

    @override
    @classmethod
    def load_this_class_from_save(cls, data: dict[str, Any]) -> Self:
        time_format = config().system.save.time_format
        slot = data["slot"]
        save_time = datetime.strptime(data["save_time"], time_format)
        nextrpg_version = data["nextrpg_version"]
        return cls(
            slot=slot, save_time=save_time, nextrpg_version=nextrpg_version
        )
