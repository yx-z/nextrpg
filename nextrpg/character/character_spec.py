from __future__ import annotations

from dataclasses import dataclass, field

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.config.character_config import CharacterConfig
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import dataclass_with_default, default
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_group import DrawingGroup


@dataclass_with_default(frozen=True)
class _BaseCharacterSpec:
    unique_name: str
    collide_with_others: bool = True
    avatar: Drawing | DrawingGroup | None = None
    display_name: str = default(lambda self: self.unique_name)
    config: CharacterConfig = field(default_factory=lambda: config().character)


@dataclass(frozen=True, kw_only=True)
class CharacterSpec(_BaseCharacterSpec):
    character: CharacterDrawing
