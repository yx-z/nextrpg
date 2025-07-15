from nextrpg.core import Pixel
from nextrpg.model import export


@export
def center_player(
    player_axis: Pixel, gui_axis: Pixel, map_axis: Pixel
) -> Pixel:
    if player_axis < gui_axis / 2:
        return 0
    if player_axis > map_axis - gui_axis / 2:
        return gui_axis - map_axis
    return gui_axis / 2 - player_axis
