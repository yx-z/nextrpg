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
        Path("assets/exterior.tmx"),
        RpgMakerCharacterDrawing.load(
            SpriteSheet(
                # Player sprite sheet.
                Drawing.load(Path("assets/fantasy/FCharacter1.png")),
                # Select a character from the sprite sheet.
                SpriteSheetSelection(row=0, column=1),
                # Declare margins to correctly detect collision/bounding box.
                margin=Margin(top=22, left=8, right=8),
            )
        ),
    )
