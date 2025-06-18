"""
Sample scene.
"""

from pathlib import Path

from nextrpg.character.rpg_maker_character_drawing import (
    Margin,
    RpgMakerCharacterDrawing,
    SpriteSheet,
    SpriteSheetSelection,
)
from nextrpg.draw_on_screen import Drawing
from nextrpg.scene.map_scene import MapScene
from nextrpg.scene.scene import Scene


def entry_scene() -> Scene:
    """
    Defines the entry scene for the game.

    Returns:
        `Scene`: The sample scene.
    """
    return MapScene.load(
        # Tiled/tmx tile map .
        Path("assets/interior.tmx"),
        RpgMakerCharacterDrawing.load(
            SpriteSheet(
                # Player sprite sheet.
                Drawing.load(Path("assets/Characters_MV.png")),
                # Select a character from the sprite sheet.
                SpriteSheetSelection(row=0, column=1),
                # Declare a 28-pixel margin to the top.
                margin=Margin(top=28),
            )
        ),
    )
