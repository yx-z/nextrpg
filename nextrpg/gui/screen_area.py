from nextrpg.config.config import config, initial_config
from nextrpg.config.window_config import ResizeMode
from nextrpg.geometry.coordinate import ORIGIN
from nextrpg.geometry.dimension import (
    HeightScaling,
    Size,
    WidthAndHeightScaling,
    WidthScaling,
)
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen


def screen_size() -> Size:
    match config().window.resize:
        case ResizeMode.SCALE:
            return initial_config().window.size
        case ResizeMode.KEEP_NATIVE_SIZE:
            return config().window.size


def window_size() -> Size:
    return config().window.size


def window_area() -> RectangleAreaOnScreen:
    size = window_size()
    return ORIGIN.anchor(size).rectangle_area_on_screen


def screen_area() -> RectangleAreaOnScreen:
    size = screen_size()
    return ORIGIN.anchor(size).rectangle_area_on_screen


def left_screen_area() -> RectangleAreaOnScreen:
    size = screen_size() / WidthScaling(2)
    return ORIGIN.anchor(size).rectangle_area_on_screen


def right_screen_area() -> RectangleAreaOnScreen:
    return left_screen_area() + screen_size().width / 2


def top_screen_area() -> RectangleAreaOnScreen:
    size = screen_size() / HeightScaling(2)
    return ORIGIN.anchor(size).rectangle_area_on_screen


def bottom_screen_area() -> RectangleAreaOnScreen:
    return top_screen_area() + screen_size().height / 2


def top_left_screen_area() -> RectangleAreaOnScreen:
    size = screen_size() / WidthAndHeightScaling(2)
    return ORIGIN.anchor(size).rectangle_area_on_screen


def top_right_screen_area() -> RectangleAreaOnScreen:
    return top_left_screen_area() + screen_size().width / 2


def bottom_left_screen_area() -> RectangleAreaOnScreen:
    return top_left_screen_area() + screen_size().height / 2


def bottom_right_screen_area() -> RectangleAreaOnScreen:
    return top_right_screen_area() + screen_size().height / 2
