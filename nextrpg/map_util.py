"""
Map utility functions for `nextrpg`.

This module provides utility functions for map-related calculations in `nextrpg`
games. It includes functions for camera positioning and player centering on
maps.

Features:
    - Player centering calculations
    - Camera positioning logic
    - Map boundary handling
    - GUI coordinate calculations
"""

from nextrpg.area import gui_size
from nextrpg.coordinate import Coordinate
from nextrpg.core import Pixel, Size
from nextrpg.model import export


@export
def center_player(player_coord: Coordinate, map_size: Size) -> Coordinate:
    map_width, map_height = map_size
    gui_width, gui_height = gui_size()
    left_shift = _center_player(player_coord.left, gui_width, map_width)
    top_shift = _center_player(player_coord.top, gui_height, map_height)
    return Coordinate(left_shift, top_shift)


def _center_player(
    player_axis: Pixel, gui_axis: Pixel, map_axis: Pixel
) -> Pixel:
    """
    Calculate the camera position to center the player on screen.

    This function calculates the optimal camera position to keep the player
    centered on screen while respecting map boundaries. It handles edge cases
    where the player is near map boundaries.

    Arguments:
        player_axis: The player's position on the given axis.
        gui_axis: The size of the GUI on the given axis.
        map_axis: The size of the map on the given axis.

    Returns:
        The camera position that centers the player.
    """
    if player_axis < gui_axis / 2:
        return 0
    if player_axis > map_axis - gui_axis / 2:
        return gui_axis - map_axis
    return gui_axis / 2 - player_axis
