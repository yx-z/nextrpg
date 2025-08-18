from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Pixel, Size
from nextrpg.gui.area import gui_height, gui_width


def center_player(player_coordinate: Coordinate, map_size: Size) -> Coordinate:
    left_shift = _center_player(
        player_coordinate.left, gui_width(), map_size.width
    )
    top_shift = _center_player(
        player_coordinate.top, gui_height(), map_size.height
    )
    return Coordinate(left_shift, top_shift)


def _center_player[T](player_axis: T, gui_axis: T, map_axis: T) -> Pixel:
    if player_axis < gui_axis / 2:
        return 0
    if player_axis > map_axis - gui_axis / 2:
        return (gui_axis - map_axis).value
    return (gui_axis / 2 - player_axis).value
