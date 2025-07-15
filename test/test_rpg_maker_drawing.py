from pygame import Surface

from nextrpg import (
    DefaultFrameType,
    RpgMakerCharacterDrawing,
    SpriteSheet,
    SpriteSheetSelection,
    XpFrameType,
    Direction,
    Size,
    Drawing,
)
from nextrpg.rpg_maker_character_drawing import _adjust


def test_rpg_maker_drawing() -> None:
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


def test_adjust() -> None:
    assert _adjust(Direction.DOWN_LEFT) is Direction.DOWN
