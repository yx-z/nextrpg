from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Pixel, Size
from nextrpg.gui.area import gui_height, gui_width


def center_player(player_coordinate: Coordinate, map_size: Size) -> Coordinate:
    left_shift = _center_player(
        player_coordinate.left_value, gui_width().value, map_size.width_value
    )
    top_shift = _center_player(
        player_coordinate.top_value, gui_height().value, map_size.height_value
    )
    return Coordinate(left_shift, top_shift)


def _center_player(
    player_axis: Pixel, gui_axis: Pixel, map_axis: Pixel
) -> Pixel:
    if player_axis < gui_axis / 2:
        return 0
    if player_axis > map_axis - gui_axis / 2:
        return gui_axis - map_axis
    return gui_axis / 2 - player_axis
