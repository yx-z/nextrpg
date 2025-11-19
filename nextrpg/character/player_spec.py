from dataclasses import dataclass, replace
from typing import Self

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_spec import CharacterSpec
from nextrpg.geometry.coordinate import Coordinate


@dataclass(frozen=True)
class PlayerSpec(CharacterSpec):
    coordinate_override: Coordinate | None = None

    def to_map(
        self, unique_name: str, character_drawing: CharacterDrawing
    ) -> Self:
        return replace(
            self,
            unique_name=unique_name,
            character_drawing=character_drawing,
            coordinate_override=None,
        )
