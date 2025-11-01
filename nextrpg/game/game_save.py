from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Self

from nextrpg.core.save import LoadFromSave, ModuleAndAttribute


@dataclass(frozen=True)
class GameSave(LoadFromSave):
    map_scene_creation_function: ModuleAndAttribute
    save_time: datetime = field(default_factory=lambda: datetime.now())

    @property
    def save_data(self) -> dict[str, Any]:
        return {
            self.map_scene_creation_function.save_key(): self.map_scene_creation_function.save_data,
            "save_time": self.save_time.strftime(_DATETIME_FORMAT),
        }

    @classmethod
    def load_from_save(cls, data: dict[str, Any]) -> Self:
        map_scene_creation_function_data = data[ModuleAndAttribute.save_key()]
        map_scene_creation_function = ModuleAndAttribute.load_from_save(
            map_scene_creation_function_data
        )

        save_time = datetime.strptime(data["save_time"], _DATETIME_FORMAT)
        return cls(
            map_scene_creation_function=map_scene_creation_function,
            save_time=save_time,
        )


_DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"
