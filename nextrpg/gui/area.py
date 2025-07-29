from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size, Pixel
from nextrpg.draw.draw import RectangleOnScreen
from nextrpg.global_config.global_config import config, initial_config
from nextrpg.global_config.gui_config import ResizeMode


def gui_size() -> Size:
    match config().gui.resize_mode:
        case ResizeMode.SCALE:
            return initial_config().gui.size
        case ResizeMode.KEEP_NATIVE_SIZE:
            return config().gui.size
    raise ValueError(f"Invalid resize mode {config().gui.resize_mode}")


def gui_width() -> Pixel:
    return gui_size().width


def gui_height() -> Pixel:
    return gui_size().height


def screen() -> RectangleOnScreen:
    return RectangleOnScreen(Coordinate(0, 0), gui_size())


def left_screen() -> RectangleOnScreen:
    coord = Coordinate(0, 0)
    size = Size(gui_size().width / 2, gui_size().height)
    return RectangleOnScreen(coord, size)


def right_screen() -> RectangleOnScreen:
    coord = Coordinate(gui_size().width / 2, 0)
    size = Size(gui_size().width / 2, gui_size().height)
    return RectangleOnScreen(coord, size)


def top_screen() -> RectangleOnScreen:
    coord = Coordinate(0, 0)
    size = Size(gui_size().width, gui_size().height / 2)
    return RectangleOnScreen(coord, size)


def bottom_screen() -> RectangleOnScreen:
    coord = Coordinate(0, gui_size().height / 2)
    size = Size(gui_size().width, gui_size().height / 2)
    return RectangleOnScreen(coord, size)


def top_left_screen() -> RectangleOnScreen:
    coord = Coordinate(0, 0)
    size = gui_size().all_dimension_scale(0.5)
    return RectangleOnScreen(coord, size)


def top_right_screen() -> RectangleOnScreen:
    coord = Coordinate(gui_size().width / 2, 0)
    size = gui_size().all_dimension_scale(0.5)
    return RectangleOnScreen(coord, size)


def bottom_left_screen() -> RectangleOnScreen:
    coord = Coordinate(0, gui_size().height / 2)
    size = gui_size().all_dimension_scale(0.5)
    return RectangleOnScreen(coord, size)


def bottom_right_screen() -> RectangleOnScreen:
    coord = Coordinate(gui_size().width / 2, gui_size().height / 2)
    size = gui_size().all_dimension_scale(0.5)
    return RectangleOnScreen(coord, size)
