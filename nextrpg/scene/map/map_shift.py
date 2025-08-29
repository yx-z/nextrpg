from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.gui.area import screen


def center_player(player_coordinate: Coordinate, map_size: Size) -> Coordinate:
    left_shift = _center_player(
        player_coordinate.left, screen().right, map_size.width.x_axis
    )
    top_shift = _center_player(
        player_coordinate.top, screen().bottom, map_size.height.y_axis
    )
    return left_shift.pair(top_shift)


def _center_player[T](player_axis: T, gui_axis: T, map_axis: T) -> T:
    if player_axis < gui_axis / 2:
        return type(player_axis)(0)
    if player_axis > map_axis - gui_axis / 2:
        return gui_axis - map_axis
    return gui_axis / 2 - player_axis
