from pygame import Surface

from nextrpg import (
    DefaultFrameType,
    Direction,
    Draw,
    RpgMakerCharacterDraw,
    Size,
    SpriteSheet,
    SpriteSheetSelection,
    Trim,
    XpFrameType,
)


def test_rpg_maker_draw() -> None:
    assert len(DefaultFrameType._frame_indices()) == 4
    assert len(DefaultFrameType) == 3
    assert len(XpFrameType._frame_indices()) == 4
    assert len(XpFrameType) == 4

    character = RpgMakerCharacterDraw(
        direction=Direction.DOWN,
        sprite_sheet=SpriteSheet(Draw(Surface((24, 16)))),
        sprite_sheet_selection=SpriteSheetSelection(0, 0),
        duration_per_frame=1,
        animate_on_idle=True,
    )
    assert character.draw.size == Size(2, 2)
    assert character.direction is Direction.DOWN
    assert character.turn(Direction.UP_RIGHT).direction is Direction.UP_RIGHT
    assert character.tick_move(2).draw.size == Size(2, 2)
    assert character.tick_idle(2).draw.size == Size(2, 2)

    character = RpgMakerCharacterDraw(
        direction=Direction.DOWN,
        sprite_sheet=SpriteSheet(Draw(Surface((24, 16)))),
        sprite_sheet_selection=SpriteSheetSelection(0, 0),
        duration_per_frame=1,
        animate_on_idle=False,
    )
    assert character.tick_idle(2).draw.size == Size(2, 2)
    assert character.turn(Direction.DOWN_LEFT)

    assert RpgMakerCharacterDraw(
        direction=Direction.DOWN,
        sprite_sheet=SpriteSheet(Draw(Surface((24, 16))), Trim(top=0)),
        duration_per_frame=1,
        animate_on_idle=False,
    )
