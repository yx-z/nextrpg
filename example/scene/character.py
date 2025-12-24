from example.scene.scene_common import IMG_DIR
from nextrpg import (
    ORIGIN,
    Coordinate,
    Drawing,
    Height,
    Padding,
    PlayerSpec,
    RpgMakerCharacterDrawing,
    RpgMakerSpriteSheet,
    SpriteSheet,
    Width,
)


def create_character_drawing(file: str) -> RpgMakerCharacterDrawing:
    path = IMG_DIR / "characters" / file
    drawing = Drawing(path)
    trim = Padding(top=Height(20), left=Width(10), right=Width(10))
    sprite_sheet = RpgMakerSpriteSheet(drawing=drawing, trim=trim)
    return RpgMakerCharacterDrawing(sprite_sheet=sprite_sheet)


def create_player_placeholder() -> PlayerSpec:
    return create_player(ORIGIN)


def create_player(
    coordinate_override: Coordinate | None = None,
) -> PlayerSpec:
    character_drawing = create_character_drawing("$PixelFantasy_1-Reid.png")

    avatar_path = IMG_DIR / "faces" / "PixelFantasy-Reid1.png"
    avatar_drawing = Drawing(avatar_path)
    avatar_sprite_sheet = SpriteSheet(
        drawing=avatar_drawing, num_rows=2, num_columns=4
    )
    avatar = avatar_sprite_sheet[0, 0]
    return PlayerSpec(
        unique_name="Reid",
        character_drawing=character_drawing,
        avatar=avatar,
        coordinate_override=coordinate_override,
    )
