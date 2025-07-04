"""
Sample scene.
"""

from collections.abc import Generator
from pathlib import Path
from typing import Any

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npc_spec import MovingNpcSpec, StaticNpcSpec
from nextrpg.character.rpg_maker_character_drawing import (
    Margin,
    RpgMakerCharacterDrawing,
    SpriteSheet,
    SpriteSheetSelection,
)
from nextrpg.core import Direction
from nextrpg.draw_on_screen import Drawing
from nextrpg.event.move import Move
from nextrpg.event.say import say
from nextrpg.scene.map_helper import MapHelper
from nextrpg.scene.map_scene import MapScene
from nextrpg.scene.scene import Scene


def interior_scene(
    player: CharacterDrawing | None = None,
    player_coordinate_object: str = "player",
) -> Scene:
    """
    Defines an interior scene.

    Arguments:
        `player`: Character drawing to use for the player.
            If `None`, a default character drawing is used.
            This allows the interior_scene to be used as the entry_scene for
            `nextrpg.Game(entry_scene)`.

        `player_coordinate_object`: Name of the object marking the initial
            coordinate of the player.

    Returns:
        `Scene`: The interior scene.
    """
    # Local import to avoid circular dependency.
    from example.exterior_scene import exterior_scene

    return MapScene(
        # Tiled/tmx tile map.
        tmx_file=Path("example/assets/interior.tmx"),
        # Use default player drawing when this scene is an entry scene.
        initial_player_drawing=player or init_player(),
        # Player coordinate on the map.
        player_coordinate_object=player_coordinate_object,
        # Move to another map.
        moves=[Move("from_interior", "to_exterior", exterior_scene)],
        static_npc_specs=[StaticNpcSpec("david", david(), greet)],
        moving_npc_specs=[MovingNpcSpec("alisa", alisa(), greet)],
    )


def greet(
    player: CharacterOnScreen,
    npc: CharacterOnScreen,
    map_helper: MapHelper,
    **kwargs: Any,
) -> Generator:
    yield say(player, "Hello World!")


def sprite_sheet() -> SpriteSheet:
    return SpriteSheet(
        # Player sprite sheet.
        Drawing("example/assets/Characters_MV.png"),
        # Declare margins to correctly detect collision/bounding box.
        margin=Margin(top=25),
    )


def init_player() -> CharacterDrawing:
    return RpgMakerCharacterDrawing(
        direction=Direction.DOWN,
        sprite_sheet=sprite_sheet(),
        # Select a character from the sprite sheet.
        sprite_sheet_selection=SpriteSheetSelection(row=0, column=0),
    )


def alisa() -> CharacterDrawing:
    return RpgMakerCharacterDrawing(
        direction=Direction.DOWN,
        sprite_sheet=sprite_sheet(),
        sprite_sheet_selection=SpriteSheetSelection(0, 1),
    )


def david() -> CharacterDrawing:
    return RpgMakerCharacterDrawing(
        direction=Direction.DOWN,
        sprite_sheet=sprite_sheet(),
        sprite_sheet_selection=SpriteSheetSelection(0, 2),
    )
