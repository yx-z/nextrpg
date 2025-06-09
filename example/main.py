"""
Example game.
"""

from pathlib import Path

from nextrpg.character.rpg_maker_drawing import (
    Margin,
    RpgMakerCharacterDrawing,
    SpriteSheet,
    SpriteSheetSelection,
)
from nextrpg.config import Config, DebugConfig, set_config
from nextrpg.draw_on_screen import Drawing
from nextrpg.scene.map_scene import MapScene
from nextrpg.scene.scene import Scene
from nextrpg.start_game import start_game


def entry_scene() -> Scene:
    """
    Return an entry scene for the game.
    The scene cannot be immediately created before `start_given`.
    This is because sprite-loading must be after pygame initialization.

    Returns:
        `Scene`: The entry scene.
    """
    return MapScene(
        # Example interior tile map created by Tiled.
        Path("assets/interior.tmx"),
        RpgMakerCharacterDrawing(
            SpriteSheet(
                # Example RPG Maker MV format character sprite sheet.
                Drawing(Path("assets/Characters_MV.png")),
                # Selects the character in the sprite sheet at row/column.
                SpriteSheetSelection(row=0, column=1),
                # 28 px margin to cut from the top.
                Margin(top=28),
            ),
        ),
    )


if __name__ == "__main__":
    # Enable debug config.
    set_config(Config(debug=DebugConfig()))
    set_config(Config())
    start_game(entry_scene)  # Start the game window and game loop.
