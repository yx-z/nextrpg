"""
NextRPG - A Python framework for building 2D role-playing games.

NextRPG provides a comprehensive toolkit for creating 2D RPG games with
Pygame. It includes character management, scene handling, event systems,
drawing utilities, and game loop management.

The framework is designed with a modular architecture that separates
concerns into distinct modules:

- `.core`: Core types and utilities used throughout the framework
- `.character`: Character drawing and movement systems
- `.scene`: Scene management and transitions
- `.event`: Event handling and processing
- `.draw`: Drawing utilities and screen rendering
- `.gui`: GUI components and window management
- `.config`: Configuration management
- `.game`: Main game loop and initialization

Example:
    ```python
    from .game import Game
    from .scene import StaticScene

    def create_entry_scene():
        return StaticScene()

    game = Game(entry_scene=create_entry_scene)
    game.start()
    ```

Version:
    Current version: 0.1.9
"""

__version__ = "0.1.9"

from nextrpg.area import *
from nextrpg.character_config import *
from nextrpg.character_drawing import *
from nextrpg.character_on_screen import *
from nextrpg.code_transformers import *
from nextrpg.global_config import *
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
from nextrpg.transition_scene import *
from nextrpg.walk import *
from nextrpg.window import *
