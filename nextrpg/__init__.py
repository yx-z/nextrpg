"""
NextRPG - A Python framework for building 2D role-playing games.

NextRPG provides a comprehensive toolkit for creating 2D RPG games with
Pygame. It includes character management, scene handling, event systems,
drawing utilities, and game loop management.

The framework is designed with a modular architecture that separates
concerns into distinct modules:

- `nextrpg.core`: Core types and utilities used throughout the framework
- `nextrpg.character`: Character drawing and movement systems
- `nextrpg.scene`: Scene management and transitions
- `nextrpg.event`: Event handling and processing
- `nextrpg.draw`: Drawing utilities and screen rendering
- `nextrpg.gui`: GUI components and window management
- `nextrpg.config`: Configuration management
- `nextrpg.game`: Main game loop and initialization

Example:
    ```python
    from nextrpg.game import Game
    from nextrpg.scene import StaticScene

    def create_entry_scene():
        return StaticScene()

    game = Game(entry_scene=create_entry_scene)
    game.start()
    ```

Version:
    Current version: 0.1.8
"""

__version__ = "0.1.8"
