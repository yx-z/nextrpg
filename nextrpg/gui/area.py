"""
Screen area utilities for `nextrpg`.

This module provides utility functions for defining screen areas and
regions in `nextrpg` games. It includes functions for getting the
logical GUI size and creating rectangles for different screen regions.

Features:
    - Logical GUI size calculation based on resize mode
    - Screen region definitions (left, right, top, bottom, corners)
    - Automatic handling of scaling vs native size modes
    - Rectangle-based area representation
"""

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size, Pixel
from nextrpg.draw.draw import RectangleOnScreen
from nextrpg.global_config.global_config import config, initial_config
from nextrpg.global_config.gui_config import ResizeMode


def gui_size() -> Size:
    """
    Get the logical size of the GUI window.

    Upon `ResizeMode.SCALE`, the logical GUI window size is the initial GUI
    size, as all scaling logic is handled internally by the `Gui` class.
    Any in-game logic of GUI size should assume the initial GUI size.

    Returns:
        The size of the GUI window.
    """
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
    """
    Get the full screen area as a rectangle.

    Returns:
        A rectangle representing the entire screen area.
    """
    return RectangleOnScreen(Coordinate(0, 0), gui_size())


def left_screen() -> RectangleOnScreen:
    """
    Get the left half of the screen as a rectangle.

    Returns:
        A rectangle representing the left half of the screen.
    """
    coord = Coordinate(0, 0)
    size = Size(gui_size().width / 2, gui_size().height)
    return RectangleOnScreen(coord, size)


def right_screen() -> RectangleOnScreen:
    """
    Get the right half of the screen as a rectangle.

    Returns:
        A rectangle representing the right half of the screen.
    """
    coord = Coordinate(gui_size().width / 2, 0)
    size = Size(gui_size().width / 2, gui_size().height)
    return RectangleOnScreen(coord, size)


def top_screen() -> RectangleOnScreen:
    """
    Get the top half of the screen as a rectangle.

    Returns:
        A rectangle representing the top half of the screen.
    """
    coord = Coordinate(0, 0)
    size = Size(gui_size().width, gui_size().height / 2)
    return RectangleOnScreen(coord, size)


def bottom_screen() -> RectangleOnScreen:
    """
    Get the bottom half of the screen as a rectangle.

    Returns:
        A rectangle representing the bottom half of the screen.
    """
    coord = Coordinate(0, gui_size().height / 2)
    size = Size(gui_size().width, gui_size().height / 2)
    return RectangleOnScreen(coord, size)


def top_left_screen() -> RectangleOnScreen:
    """
    Get the top-left quarter of the screen as a rectangle.

    Returns:
        A rectangle representing the top-left quarter of the screen.
    """
    coord = Coordinate(0, 0)
    size = gui_size().all_dimension_scale(0.5)
    return RectangleOnScreen(coord, size)


def top_right_screen() -> RectangleOnScreen:
    """
    Get the top-right quarter of the screen as a rectangle.

    Returns:
        A rectangle representing the top-right quarter of the screen.
    """
    coord = Coordinate(gui_size().width / 2, 0)
    size = gui_size().all_dimension_scale(0.5)
    return RectangleOnScreen(coord, size)


def bottom_left_screen() -> RectangleOnScreen:
    """
    Get the bottom-left quarter of the screen as a rectangle.

    Returns:
        A rectangle representing the bottom-left quarter of the screen.
    """
    coord = Coordinate(0, gui_size().height / 2)
    size = gui_size().all_dimension_scale(0.5)
    return RectangleOnScreen(coord, size)


def bottom_right_screen() -> RectangleOnScreen:
    """
    Get the bottom-right quarter of the screen as a rectangle.

    Returns:
        A rectangle representing the bottom-right quarter of the screen.
    """
    coord = Coordinate(gui_size().width / 2, gui_size().height / 2)
    size = gui_size().all_dimension_scale(0.5)
    return RectangleOnScreen(coord, size)
