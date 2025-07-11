from nextrpg.config import ResizeMode, config, initial_config
from nextrpg.core import Size
from nextrpg.draw.coordinate import Coordinate
from nextrpg.draw.draw_on_screen import Rectangle


def gui_size() -> Size:
    """
    Get the logical size of the GUI window.
    Upon ResizeMode.SCALE, the logical GUI window size shall be the initial
    GUI size given all the scaling logic of game content is handled already
    at `Gui` class internally.

    So any in-game logic of GUI size shall assume the initial GUI size.

    Returns:
        `Size`: The size of the GUI window.
    """
    match config().gui.resize_mode:
        case ResizeMode.SCALE:
            return initial_config().gui.size
        case ResizeMode.KEEP_NATIVE_SIZE:
            return config().gui.size
    raise ValueError(f"Invalid resize mode {config().gui.resize_mode}")


def screen() -> Rectangle:
    return Rectangle(Coordinate(0, 0), gui_size())


def left_screen() -> Rectangle:
    size = Size(gui_size().width / 2, gui_size().height)
    return Rectangle(Coordinate(0, 0), size)


def right_screen() -> Rectangle:
    size = Size(gui_size().width / 2, gui_size().height)
    return Rectangle(Coordinate(gui_size().width / 2, 0), size)


def top_screen() -> Rectangle:
    size = Size(gui_size().width, gui_size().height / 2)
    return Rectangle(Coordinate(0, 0), size)


def bottom_screen() -> Rectangle:
    size = Size(gui_size().width, gui_size().height / 2)
    return Rectangle(Coordinate(0, gui_size().height / 2), size)


def top_left_screen() -> Rectangle:
    size = Size(gui_size().width / 2, gui_size().height / 2)
    return Rectangle(Coordinate(0, 0), size)


def top_right_screen() -> Rectangle:
    size = Size(gui_size().width / 2, gui_size().height / 2)
    return Rectangle(Coordinate(gui_size().width / 2, 0), size)


def bottom_left_screen() -> Rectangle:
    size = Size(gui_size().width / 2, gui_size().height / 2)
    return Rectangle(Coordinate(0, gui_size().height / 2), size)


def bottom_right_screen() -> Rectangle:
    size = Size(gui_size().width / 2, gui_size().height / 2)
    return Rectangle(
        Coordinate(gui_size().width / 2, gui_size().height / 2), size
    )
