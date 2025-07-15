"""
Screen area utilities for NextRPG.

This module provides utility functions for defining screen areas and
regions in NextRPG games. It includes functions for getting the
logical GUI size and creating rectangles for different screen regions.

The area system features:
- Logical GUI size calculation based on resize mode
- Screen region definitions (left, right, top, bottom, corners)
- Automatic handling of scaling vs native size modes
- Rectangle-based area representation

Example:
    ```python
    from nextrpg.area import gui_size, left_screen, top_right_screen

    # Get the logical GUI size
    size = gui_size()

    # Get screen regions
    left_half = left_screen()
    top_right = top_right_screen()
    ```
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

    Upon `ResizeMode.SCALE`, the logical GUI window size shall be the initial
    GUI size given all the scaling logic of game content is handled already
    at `Gui` class internally.

    So any in-game logic of GUI size shall assume the initial GUI size.

    Returns:
        `Size`: The size of the GUI window.

    Example:
        ```python
        from nextrpg.area import gui_size

        # Get the logical GUI size
        size = gui_size()
        width, height = size
        ```
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
        `Rectangle`: A rectangle representing the entire screen area.

    Example:
        ```python
        from nextrpg.area import screen

        # Get the full screen area
        full_screen = screen()
        ```
    """
    return Rectangle(Coordinate(0, 0), gui_size())


@export
def left_screen() -> Rectangle:
    """
    Get the left half of the screen as a rectangle.

    Returns:
        `Rectangle`: A rectangle representing the left half of the screen.

    Example:
        ```python
        from nextrpg.area import left_screen

        # Get the left half of the screen
        left_half = left_screen()
        ```
    """
    size = Size(gui_size().width / 2, gui_size().height)
    return Rectangle(Coordinate(0, 0), size)


@export
def right_screen() -> Rectangle:
    """
    Get the right half of the screen as a rectangle.

    Returns:
        `Rectangle`: A rectangle representing the right half of the screen.

    Example:
        ```python
        from nextrpg.area import right_screen

        # Get the right half of the screen
        right_half = right_screen()
        ```
    """
    size = Size(gui_size().width / 2, gui_size().height)
    return Rectangle(Coordinate(gui_size().width / 2, 0), size)


@export
def top_screen() -> Rectangle:
    """
    Get the top half of the screen as a rectangle.

    Returns:
        `Rectangle`: A rectangle representing the top half of the screen.

    Example:
        ```python
        from nextrpg.area import top_screen

        # Get the top half of the screen
        top_half = top_screen()
        ```
    """
    size = Size(gui_size().width, gui_size().height / 2)
    return Rectangle(Coordinate(0, 0), size)


@export
def bottom_screen() -> Rectangle:
    """
    Get the bottom half of the screen as a rectangle.

    Returns:
        `Rectangle`: A rectangle representing the bottom half of the screen.

    Example:
        ```python
        from nextrpg.area import bottom_screen

        # Get the bottom half of the screen
        bottom_half = bottom_screen()
        ```
    """
    size = Size(gui_size().width, gui_size().height / 2)
    return Rectangle(Coordinate(0, gui_size().height / 2), size)


@export
def top_left_screen() -> Rectangle:
    """
    Get the top-left quarter of the screen as a rectangle.

    Returns:
        `Rectangle`: A rectangle representing the top-left quarter of the screen.

    Example:
        ```python
        from nextrpg.area import top_left_screen

        # Get the top-left quarter
        top_left = top_left_screen()
        ```
    """
    size = Size(gui_size().width / 2, gui_size().height / 2)
    return Rectangle(Coordinate(0, 0), size)


@export
def top_right_screen() -> Rectangle:
    """
    Get the top-right quarter of the screen as a rectangle.

    Returns:
        `Rectangle`: A rectangle representing the top-right quarter of the screen.

    Example:
        ```python
        from nextrpg.area import top_right_screen

        # Get the top-right quarter
        top_right = top_right_screen()
        ```
    """
    size = Size(gui_size().width / 2, gui_size().height / 2)
    return Rectangle(Coordinate(gui_size().width / 2, 0), size)


@export
def bottom_left_screen() -> Rectangle:
    """
    Get the bottom-left quarter of the screen as a rectangle.

    Returns:
        `Rectangle`: A rectangle representing the bottom-left quarter of the screen.

    Example:
        ```python
        from nextrpg.area import bottom_left_screen

        # Get the bottom-left quarter
        bottom_left = bottom_left_screen()
        ```
    """
    size = Size(gui_size().width / 2, gui_size().height / 2)
    return Rectangle(Coordinate(0, gui_size().height / 2), size)


@export
def bottom_right_screen() -> Rectangle:
    """
    Get the bottom-right quarter of the screen as a rectangle.

    Returns:
        `Rectangle`: A rectangle representing the bottom-right quarter of the screen.

    Example:
        ```python
        from nextrpg.area import bottom_right_screen

        # Get the bottom-right quarter
        bottom_right = bottom_right_screen()
        ```
    """
    size = Size(gui_size().width / 2, gui_size().height / 2)
    return Rectangle(
        Coordinate(gui_size().width / 2, gui_size().height / 2), size
    )
