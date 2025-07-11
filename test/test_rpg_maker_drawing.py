from pygame import Surface

from nextrpg.character.rpg_maker_character_drawing import (
    DefaultFrameType,
    RpgMakerCharacterDrawing,
    SpriteSheet,
    SpriteSheetSelection,
    XpFrameType,
)
from nextrpg.core import Direction, Size
from nextrpg.draw.draw_on_screen import Drawing


def test_rpg_maker_drawing():
    assert len(DefaultFrameType._frame_indices()) == 4
    assert len(DefaultFrameType) == 3
    assert len(XpFrameType._frame_indices()) == 4
    assert len(XpFrameType) == 4

    character = RpgMakerCharacterDrawing(
        direction=Direction.DOWN,
        sprite_sheet=SpriteSheet(Drawing(Surface((24, 16)))),
        sprite_sheet_selection=SpriteSheetSelection(0, 0),
        duration_per_frame=1,
        animate_on_idle=True,
    )
    assert character.drawing.size == Size(2, 2)
    assert character.direction is Direction.DOWN
    assert character.turn(Direction.UP_RIGHT).direction is Direction.UP_RIGHT
    assert character.tick_move(2).drawing.size == Size(2, 2)
    assert character.tick_idle(2).drawing.size == Size(2, 2)

    character = RpgMakerCharacterDrawing(
        direction=Direction.DOWN,
        sprite_sheet=SpriteSheet(Drawing(Surface((24, 16)))),
        sprite_sheet_selection=SpriteSheetSelection(0, 0),
        duration_per_frame=1,
        animate_on_idle=False,
    )
    assert character.tick_idle(2).drawing.size == Size(2, 2)
