from nextrpg.common_types import (
    CharacterSprite,
    Coordinate,
    Direction,
    Millesecond,
)
from nextrpg.drawable import Drawable


class Character:
    def __init__(
        self,
        character_sprite: CharacterSprite,
        coordinate: Coordinate,
        direction: Direction,
    ) -> None:
        self.character_sprite = character_sprite
        self.coordinate = coordinate
        self.direction = direction

    def draw(self, time: Millesecond) -> list[Drawable]:
        return [
            Drawable(
                self.character_sprite.draw(time, self.direction),
                self.coordinate,
            )
        ]
