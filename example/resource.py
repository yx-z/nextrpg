from functools import cache
from pathlib import Path

from nextrpg import (
    CharacterSpec,
    Direction,
    Drawing,
    DrawingTrim,
    Height,
    RpgMakerCharacterDrawing,
    RpgMakerSpriteSheet,
    SpriteSheetSelection,
)


@cache
def sprite_sheet() -> RpgMakerSpriteSheet:
    sprite_sheet_drawing = Drawing(Path("example/asset/Characters_MV.png"))
    sprite_sheet_trim = DrawingTrim(top=Height(25))
    return RpgMakerSpriteSheet(
        drawing=sprite_sheet_drawing, trim=sprite_sheet_trim
    )


def create_player() -> CharacterSpec:
    player_drawing = RpgMakerCharacterDrawing(
        Direction.DOWN,
        sprite_sheet(),
        SpriteSheetSelection(row=0, column=0),
    )
    avatar = Drawing(Path("example/asset/avatar.png"))
    return CharacterSpec(
        unique_name="player",
        display_name="Will",
        character=player_drawing,
        avatar=avatar,
    )
