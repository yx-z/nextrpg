"""
Configuration management system for NextRPG.

This module provides a comprehensive configuration management system
for NextRPG games. It includes configuration classes for all major
game systems, with support for loading, validation, and runtime
updates.

The configuration system includes:
- `config`: Main configuration management and loading
- `gui_config`: GUI and window configuration
- `debug_config`: Debug logging and development settings
- `key_mapping_config`: Keyboard and input mapping
- `character_config`: Character and sprite configuration
- `text_config`: Text rendering and font settings
- `event_config`: Event handling configuration
- `resource_config`: Resource loading and management
- `tile_map_config`: Tile map and level configuration
- `transition_config`: Scene transition settings
- `draw_on_screen_config`: Drawing and rendering settings
- `say_event_config`: Dialog and text event settings
- `rpg_maker_character_drawing_config`: RPG Maker sprite settings

The configuration system is designed to provide centralized
management of all game settings, with support for different
environments (development, production) and runtime updates.

Example:
    ```python
    from nextrpg.config import config
    from nextrpg.config.gui_config import GuiConfig

    # Access global configuration
    settings = config()

    # Get specific configuration
    gui_settings = settings.gui

    # Update configuration
    new_gui = GuiConfig(frames_per_second=60)
    ```
"""
