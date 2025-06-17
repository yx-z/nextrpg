from pygame import Surface

from nextrpg.character.rpg_maker_character_drawing import (
    RpgMakerCharacterDrawing,
    SpriteSheet,
    SpriteSheetSelection,
)
from nextrpg.common_types import Direction, Size
from nextrpg.draw_on_screen import Drawing


def test_rpg_maker_drawing():
    character = RpgMakerCharacterDrawing.load(
        SpriteSheet(Drawing(Surface((24, 16))), SpriteSheetSelection(0, 0)),
        frame_duration=1,
        animate_on_idle=True,
    )
    assert character.drawing.size == Size(2, 2)
    assert character.direction is Direction.DOWN
    assert character.turn(Direction.UP_RIGHT).direction is Direction.UP_RIGHT
    assert character.move(2).drawing.size == Size(2, 2)
    assert character.idle(2).drawing.size == Size(2, 2)
