from dataclasses import dataclass, field, replace
from typing import Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.config.character.behavior_config import BehaviorConfig
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import dataclass_with_default, default
from nextrpg.core.save import UpdateFromSave
from nextrpg.drawing.sprite import Sprite


@dataclass_with_default(frozen=True)
class _BaseCharacterSpec(UpdateFromSave[str]):
    unique_name: str
    collide_with_others: bool = True
    avatar: Sprite | None = None
    display_name: str = default(lambda self: self.unique_name)
    config: BehaviorConfig = field(
        default_factory=lambda: config().character.behavior
    )

    @override
    def save_data_this_class(self) -> str:
        return self.unique_name

    @override
    def update_this_class_from_save(self, data: str) -> Self:
        return replace(self, unique_name=data)


@dataclass(frozen=True, kw_only=True)
class CharacterSpec(_BaseCharacterSpec):
    character_drawing: CharacterDrawing
