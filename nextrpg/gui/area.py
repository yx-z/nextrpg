from nextrpg.config.config import config, initial_config
from nextrpg.config.window_config import ResizeMode
from nextrpg.geometry.coordinate import ORIGIN
from nextrpg.geometry.dimension import (
    Height,
    HeightScaling,
    Size,
    Width,
    WidthAndHeightScaling,
    WidthScaling,
)
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen


def gui_size() -> Size:
    match config().window.resize:
        case ResizeMode.SCALE:
            return initial_config().window.size
        case ResizeMode.KEEP_NATIVE_SIZE:
            return config().window.size


def gui_width() -> Width:
    return gui_size().width


def gui_height() -> Height:
    return gui_size().height


def screen() -> RectangleAreaOnScreen:
    return RectangleAreaOnScreen(ORIGIN, gui_size())


def left_screen() -> RectangleAreaOnScreen:
    return RectangleAreaOnScreen(ORIGIN, gui_size() / WidthScaling(2))


def right_screen() -> RectangleAreaOnScreen:
    return left_screen() + gui_size().width / 2


def top_screen() -> RectangleAreaOnScreen:
    return RectangleAreaOnScreen(ORIGIN, gui_size() / HeightScaling(2))


def bottom_screen() -> RectangleAreaOnScreen:
    return top_screen() + gui_size().height / 2


def top_left_screen() -> RectangleAreaOnScreen:
    return RectangleAreaOnScreen(ORIGIN, gui_size() / WidthAndHeightScaling(2))


def top_right_screen() -> RectangleAreaOnScreen:
    return top_left_screen() + gui_size().width / 2


def bottom_left_screen() -> RectangleAreaOnScreen:
    return top_left_screen() + gui_size().height / 2


def bottom_right_screen() -> RectangleAreaOnScreen:
    return top_right_screen() + gui_size().height / 2
