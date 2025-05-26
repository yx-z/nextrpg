from pathlib import Path

from nextrpg.config import Config
from nextrpg.map_scene import MapScene
from nextrpg.rpg_maker_sprite_sheet import (
    RpgMakerCharacterSprite,
    SpriteSheet,
    SpriteSheetSelection,
)
from nextrpg.start_game import start_game


def main() -> None:
    config = Config()
    start_game(
        config.gui,
        lambda: MapScene(
            config.map,
            Path("assets/interior.tmx"),
            RpgMakerCharacterSprite(
                SpriteSheet(
                    Path("assets/Characters_MV.png"), SpriteSheetSelection(0, 0)
                ),
                animate_on_idle=True,
            ),
        ),
    )


if __name__ == "__main__":
    main()
