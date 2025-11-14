from dataclasses import dataclass, field, replace
from typing import Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.config.character.character_config import CharacterConfig
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import dataclass_with_default, default
from nextrpg.core.save import UpdateFromSave
from nextrpg.drawing.animation_like import AnimationLike


@dataclass_with_default(frozen=True)
class _BaseCharacterSpec(UpdateFromSave[str]):
    unique_name: str
    collide_with_others: bool = True
    avatar: AnimationLike | None = None
    display_name: str = default(lambda self: self.unique_name)
    config: CharacterConfig = field(default_factory=lambda: config().character)

    @override
    def _save_data(self) -> str:
        return self.unique_name

    @override
    def _update_from_save(self, data: str) -> Self:
        return replace(self, unique_name=data)


@dataclass(frozen=True, kw_only=True)
class CharacterSpec(_BaseCharacterSpec):
    character_drawing: CharacterDrawing
