"""NextRPG - A Python framework for building 2D role-playing games.

NextRPG provides a comprehensive toolkit for creating 2D RPG games with
Pygame. It includes character management, scene handling, event systems,
drawing utilities, and game loop management.

The framework is designed with a modular architecture that separates
concerns into distinct modules:

Core Components:
    - `.core`: Core types and utilities used throughout the framework
    - `.character`: Character drawing and movement systems
    - `.scene`: Scene management and transitions
    - `.event`: Event handling and processing
    - `.draw`: Drawing utilities and screen rendering
    - `.gui`: GUI components and window management
    - `.global_config`: Configuration management
    - `.game`: Main game loop and initialization

Key Features:
    - TMX map loading and rendering with Tiled support
    - Character movement with collision detection and pathfinding
    - Event-driven dialogue and interaction systems
    - Scene transitions and animations (fade in/out, etc.)
    - Configurable input mapping and key bindings
    - Debug visualization tools and logging
    - RPG Maker sprite sheet compatibility
    - NPC management and AI behaviors
    - Text rendering and dialogue systems
    - Resource management and asset loading

Architecture:
    The framework follows a component-based architecture where:
    - Scenes manage the game state and coordinate between components
    - Characters handle movement, drawing, and interaction logic
    - Events provide a flexible system for game interactions
    - Drawing utilities abstract pygame rendering operations
    - Configuration system allows easy customization

Example Usage:
    ```python
    from nextrpg.game import Game
    from nextrpg.scene import StaticScene
    from nextrpg.character_drawing import CharacterDrawing
    from nextrpg.coordinate import Coordinate
    from nextrpg.direction import Direction

    def create_entry_scene():
        # Create a simple scene with a character
        character = CharacterDrawing(
            drawing=load_sprite("player.png"),
            direction=Direction.DOWN
        )
        return StaticScene()

    # Initialize and start the game
    game = Game(entry_scene=create_entry_scene)
    game.start()
    ```

Advanced Example:
    ```python
    from nextrpg.map_scene import MapScene
    from nextrpg.npcs import NpcSpec, EventfulScene
    from nextrpg.say_event import say_event

    def create_town_scene():
        # Create NPCs with events
        shopkeeper = NpcSpec(
            name="Shopkeeper",
            drawing=load_character("shopkeeper.png"),
            event=shop_dialog_event
        )

        # Create map scene with NPCs
        return EventfulScene(
            player=player,
            npcs=(shopkeeper,)
        )

    def shop_dialog_event(player, npc, scene):
        yield say_event("Welcome to my shop!")
        yield say_event("What would you like to buy?")
    ```

Version:
    Current version: 0.1.12

Dependencies:
    - pygame: For graphics and input handling
    - tmx: For map loading and rendering
    - typing: For type annotations
    - dataclasses: For data structures
    - functools: For utility functions
"""

__version__ = "0.1.12"

from nextrpg.character.character_drawing import *
from nextrpg.character.character_on_screen import *
from nextrpg.character.moving_character_on_screen import *
from nextrpg.character.moving_npc_on_screen import *
from nextrpg.character.npc_on_screen import *
from nextrpg.character.player_on_screen import *
from nextrpg.character.rpg_maker_character_drawing import *
from nextrpg.core.cached_decorator import *
from nextrpg.core.coordinate import *
from nextrpg.core.dimension import *
from nextrpg.core.logger import *
from nextrpg.core.dataclass_with_instance_init import *
from nextrpg.core.walk import *
from nextrpg.draw.color import *
from nextrpg.draw.cyclic_frames import *
from nextrpg.draw.draw_on_screen import *
from nextrpg.draw.fade import *
from nextrpg.draw.text import *
from nextrpg.draw.text_on_screen import *
from nextrpg.draw.typewriter import *
from nextrpg.event.code_transformers import *
from nextrpg.event.event_as_attr import *
from nextrpg.event.event_transformer import *
from nextrpg.event.pygame_event import *
from nextrpg.event.rpg_event import *
from nextrpg.game import *
from nextrpg.global_config.character_config import *
from nextrpg.global_config.debug_config import *
from nextrpg.global_config.draw_on_screen_config import *
from nextrpg.global_config.event_config import *
from nextrpg.global_config.global_config import *
from nextrpg.global_config.gui_config import *
from nextrpg.global_config.key_mapping_config import *
from nextrpg.global_config.resource_config import *
from nextrpg.global_config.rpg_maker_character_drawing_config import *
from nextrpg.global_config.say_event_config import *
from nextrpg.global_config.text_config import *
from nextrpg.global_config.tile_map_config import *
from nextrpg.global_config.transition_config import *
from nextrpg.gui import *
from nextrpg.gui.area import *
from nextrpg.gui.window import *
from nextrpg.scene import *
from nextrpg.scene.map_helper import *
from nextrpg.scene.map_scene import *
from nextrpg.scene.map_util import *
from nextrpg.scene.say_event_scene import *
from nextrpg.scene.say_event_scene_add_on import *
from nextrpg.scene.transition_scene import *
