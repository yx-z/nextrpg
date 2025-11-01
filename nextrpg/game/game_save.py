from dataclasses import dataclass, field
from datetime import datetime
from functools import cached_property
from typing import Any, Self

from nextrpg.config.config import config
from nextrpg.config.save_config import SaveConfig
from nextrpg.core.save import LoadFromSave, ModuleAndAttribute


@dataclass(frozen=True)
class GameSave(LoadFromSave):
    scene_creation_function: ModuleAndAttribute
    save_time: datetime = field(default_factory=lambda: datetime.now())
    config: SaveConfig = field(default_factory=lambda: config().save)

    @cached_property
    def save_time_str(self) -> str:
        return self.save_time.strftime(self.config.save_time_str_format)

    @property
    def save_data(self) -> dict[str, Any]:
        return {
            ModuleAndAttribute.save_key(): self.scene_creation_function.save_data,
            "save_time": self.save_time.strftime(
                self.config.save_time_str_format
            ),
        }

    @classmethod
    def load_from_save(cls, data: dict[str, Any]) -> Self:
        scene_creation_function_data = data[ModuleAndAttribute.save_key()]
        scene_creation_function = ModuleAndAttribute.load_from_save(
            scene_creation_function_data
        )

        save_time_format = config().save.save_time_str_format
        save_time = datetime.strptime(data["save_time"], save_time_format)
        return cls(
            scene_creation_function=scene_creation_function, save_time=save_time
        )
