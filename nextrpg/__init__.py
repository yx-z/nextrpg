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
    - `.config`: Configuration management
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
    Current version: 0.1.10

Dependencies:
    - pygame: For graphics and input handling
    - tmx: For map loading and rendering
    - typing: For type annotations
    - dataclasses: For data structures
    - functools: For utility functions
"""

__version__ = "0.1.10"

from nextrpg.area import *
from nextrpg.character_config import *
from nextrpg.character_drawing import *
from nextrpg.character_on_screen import *
from nextrpg.code_transformers import *
from nextrpg.coordinate import *
from nextrpg.core import *
from nextrpg.debug_config import *
from nextrpg.draw_on_screen import *
from nextrpg.draw_on_screen_config import *
from nextrpg.event_as_attr import *
from nextrpg.event_config import *
from nextrpg.event_transformer import *
from nextrpg.fade import *
from nextrpg.fade_in import *
from nextrpg.fade_out import *
from nextrpg.frames import *
from nextrpg.game import *
from nextrpg.global_config import *
from nextrpg.gui_config import *
from nextrpg.key_mapping_config import *
from nextrpg.logger import *
from nextrpg.map_helper import *
from nextrpg.map_scene import *
from nextrpg.map_util import *
from nextrpg.model import *
from nextrpg.moving_character_on_screen import *
from nextrpg.moving_npc import *
from nextrpg.npcs import *
from nextrpg.player_on_screen import *
from nextrpg.plugins import *
from nextrpg.pygame_event import *
from nextrpg.resource_config import *
from nextrpg.rpg_event import *
from nextrpg.rpg_maker_character_drawing import *
from nextrpg.rpg_maker_character_drawing_config import *
from nextrpg.say_event import *
from nextrpg.say_event_config import *
from nextrpg.scene import *
from nextrpg.static_scene import *
from nextrpg.text import *
from nextrpg.text_config import *
from nextrpg.text_on_screen import *
from nextrpg.tile_map_config import *
from nextrpg.transition_config import *
from nextrpg.transition_scene import *
from nextrpg.walk import *
from nextrpg.gui import *
