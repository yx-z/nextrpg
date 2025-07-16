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

from nextrpg.coordinate import Coordinate
from nextrpg.core import Size
from nextrpg.draw_on_screen import Rectangle
from nextrpg.global_config import config, initial_config
from nextrpg.gui_config import ResizeMode
from nextrpg.model import export


@export
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


@export
def screen() -> Rectangle:
    """
    Get the full screen area as a rectangle.

    Returns:
        A rectangle representing the entire screen area.
    """
    return Rectangle(Coordinate(0, 0), gui_size())


@export
def left_screen() -> Rectangle:
    """
    Get the left half of the screen as a rectangle.

    Returns:
        A rectangle representing the left half of the screen.
    """
    size = Size(gui_size().width / 2, gui_size().height)
    return Rectangle(Coordinate(0, 0), size)


@export
def right_screen() -> Rectangle:
    """
    Get the right half of the screen as a rectangle.

    Returns:
        A rectangle representing the right half of the screen.
    """
    size = Size(gui_size().width / 2, gui_size().height)
    return Rectangle(Coordinate(gui_size().width / 2, 0), size)


@export
def top_screen() -> Rectangle:
    """
    Get the top half of the screen as a rectangle.

    Returns:
        A rectangle representing the top half of the screen.
    """
    size = Size(gui_size().width, gui_size().height / 2)
    return Rectangle(Coordinate(0, 0), size)


@export
def bottom_screen() -> Rectangle:
    """
    Get the bottom half of the screen as a rectangle.

    Returns:
        A rectangle representing the bottom half of the screen.
    """
    size = Size(gui_size().width, gui_size().height / 2)
    return Rectangle(Coordinate(0, gui_size().height / 2), size)


@export
def top_left_screen() -> Rectangle:
    """
    Get the top-left quarter of the screen as a rectangle.

    Returns:
        A rectangle representing the top-left quarter of the screen.
    """
    size = Size(gui_size().width / 2, gui_size().height / 2)
    return Rectangle(Coordinate(0, 0), size)


@export
def top_right_screen() -> Rectangle:
    """
    Get the top-right quarter of the screen as a rectangle.

    Returns:
        A rectangle representing the top-right quarter of the screen.
    """
    size = Size(gui_size().width / 2, gui_size().height / 2)
    return Rectangle(Coordinate(gui_size().width / 2, 0), size)


@export
def bottom_left_screen() -> Rectangle:
    """
    Get the bottom-left quarter of the screen as a rectangle.

    Returns:
        A rectangle representing the bottom-left quarter of the screen.
    """
    size = Size(gui_size().width / 2, gui_size().height / 2)
    return Rectangle(Coordinate(0, gui_size().height / 2), size)


@export
def bottom_right_screen() -> Rectangle:
    """
    Get the bottom-right quarter of the screen as a rectangle.

    Returns:
        A rectangle representing the bottom-right quarter of the screen.
    """
    size = Size(gui_size().width / 2, gui_size().height / 2)
    return Rectangle(
        Coordinate(gui_size().width / 2, gui_size().height / 2), size
    )
