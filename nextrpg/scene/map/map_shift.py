from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Pixel, Size
from nextrpg.gui.area import gui_size


def center_player(player_coord: Coordinate, map_size: Size) -> Coordinate:
    map_width, map_height = map_size
    gui_width, gui_height = gui_size()
    left_shift = _center_player(player_coord.left, gui_width, map_width)
    top_shift = _center_player(player_coord.top, gui_height, map_height)
    return Coordinate(left_shift, top_shift)


def _center_player(
    player_axis: Pixel, gui_axis: Pixel, map_axis: Pixel
) -> Pixel:
    if player_axis < gui_axis / 2:
        return 0
    if player_axis > map_axis - gui_axis / 2:
        return gui_axis - map_axis
    return gui_axis / 2 - player_axis
