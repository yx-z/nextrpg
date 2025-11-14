from collections.abc import Callable
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Self, override

from nextrpg import to_module_and_attribute
from nextrpg.core.module_and_attribute import ModuleAndAttribute
from nextrpg.core.save import HasSaveData, LoadSavable
from nextrpg.scene.scene import Scene


class SceneWithCreationFunction[Context](HasSaveData, Scene):
    creation_function: ModuleAndAttribute[Callable[[Context], Self]]


@dataclass(frozen=True)
class GameSave[Context](LoadSavable):
    context_creation: Callable[[], Context]
    scene: SceneWithCreationFunction[Context]

    @override
    @cached_property
    def _save_data(self) -> dict[str, Any]:
        scene_creation = self.scene.creation_function
        context_creation = to_module_and_attribute(self.context_creation)
        return {
            "scene": self.scene.save_data,
            "context_creation": context_creation.save_data,
            "scene_creation": scene_creation.save_data,
        }

    @override
    @classmethod
    def _load_from_save(cls, data: dict[str, Any]) -> Self:
        scene_creation = ModuleAndAttribute.load_from_save(
            data["scene_creation"]
        )
        context_creation = ModuleAndAttribute.load_from_save(
            data["context_creation"]
        )

        context = context_creation.imported()
        scene = scene_creation.imported(context)
        saved_scene = scene.update_from_save(data["scene"])
        return cls(context_creation=context_creation, scene=saved_scene)
