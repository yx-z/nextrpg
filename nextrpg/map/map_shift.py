from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Pixel
from nextrpg.geometry.size import Size
from nextrpg.gui.screen_area import screen_size


def center_player(player_center: Coordinate, map_size: Size) -> Coordinate:
    left_shift = _center_player(
        player_center.left_value,
        screen_size().width_value,
        map_size.width_value,
    )
    top_shift = _center_player(
        player_center.top_value,
        screen_size().height_value,
        map_size.height_value,
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
