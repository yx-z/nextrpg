"""
Scene management system for NextRPG.

This module provides a comprehensive scene management system for NextRPG
games. It includes scene base classes, map scenes, static scenes,
transitions, and utility functions for scene handling.

The scene system includes:
- `scene`: Base scene class and scene management
- `static_scene`: Simple static scenes without movement
- `map_scene`: Map-based scenes with tile rendering
- `map_helper`: Utilities for map loading and processing
- `map_util`: Additional map utility functions
- `transition_scene`: Scene transition effects
- `transition_triple`: Triple-buffer transition system

The scene system is designed to handle different types of game scenes,
from simple static screens to complex map-based environments with
smooth transitions between scenes.

Example:
    ```python
    from nextrpg.scene import Scene, StaticScene, MapScene

    # Create a simple static scene
    scene = StaticScene()

    # Create a map-based scene
    map_scene = MapScene("maps/town.tmx")

    # Handle scene transitions
    scene = scene.tick(time_delta)
    ```
"""
