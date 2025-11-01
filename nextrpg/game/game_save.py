from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Self

from nextrpg.core.save import LoadFromSave, ModuleAndAttribute


@dataclass(frozen=True)
class GameSave(LoadFromSave):
    scene_creation_function: ModuleAndAttribute
    save_time: datetime = field(default_factory=lambda: datetime.now())

    @property
    def save_data(self) -> dict[str, Any]:
        return {
            ModuleAndAttribute.save_key(): self.scene_creation_function.save_data,
            "save_time": self.save_time.strftime(_DATETIME_FORMAT),
        }

    @classmethod
    def load_from_save(cls, data: dict[str, Any]) -> Self:
        scene_creation_function_data = data[ModuleAndAttribute.save_key()]
        scene_creation_function = ModuleAndAttribute.load_from_save(
            scene_creation_function_data
        )

        save_time = datetime.strptime(data["save_time"], _DATETIME_FORMAT)
        return cls(
            scene_creation_function=scene_creation_function, save_time=save_time
        )


_DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"
