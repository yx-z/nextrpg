"""
Map utility functions for NextRPG.

This module provides utility functions for map-related calculations
in NextRPG games. It includes functions for camera positioning
and player centering on maps.

The map utility system features:
- Player centering calculations
- Camera positioning logic
- Map boundary handling
- GUI coordinate calculations

Example:
    ```python
    from nextrpg.map_util import center_player
    from nextrpg.core import Pixel

    # Center player on screen
    camera_x = center_player(player_x, gui_width, map_width)
    camera_y = center_player(player_y, gui_height, map_height)
    ```
"""

from nextrpg.core import Pixel
from nextrpg.model import export


@export
def center_player(
    player_axis: Pixel, gui_axis: Pixel, map_axis: Pixel
) -> Pixel:
    """
    Calculate the camera position to center the player on screen.

    This function calculates the optimal camera position to keep
    the player centered on screen while respecting map boundaries.
    It handles edge cases where the player is near map boundaries.

    Arguments:
        `player_axis`: The player's position on the given axis.

        `gui_axis`: The size of the GUI on the given axis.

        `map_axis`: The size of the map on the given axis.

    Returns:
        `Pixel`: The camera position that centers the player.

    Example:
        ```python
        from nextrpg.map_util import center_player
        from nextrpg.core import Pixel

        # Center player horizontally
        camera_x = center_player(player_x, gui_width, map_width)

        # Center player vertically
        camera_y = center_player(player_y, gui_height, map_height)
        ```
    """
    if player_axis < gui_axis / 2:
        return 0
    if player_axis > map_axis - gui_axis / 2:
        return gui_axis - map_axis
    return gui_axis / 2 - player_axis
