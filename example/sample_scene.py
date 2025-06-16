"""
Sample scene.
"""

from pathlib import Path

from nextrpg.character.rpg_maker_drawing import (
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
        Path("assets/interior.tmx"),
        RpgMakerCharacterDrawing.load(
            SpriteSheet(
                Drawing.load(Path("assets/Characters_MV.png")),
                SpriteSheetSelection(row=0, column=1),
            )
        ),
    )
