from nextrpg.config.config import initial_config
from nextrpg.geometry.coordinate import ORIGIN
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.geometry.scaling import (
    HeightScaling,
    WidthAndHeightScaling,
    WidthScaling,
)
from nextrpg.geometry.size import Size


def screen_size() -> Size:
    return initial_config().system.window.size


def screen_area() -> RectangleAreaOnScreen:
    size = screen_size()
    return ORIGIN.as_top_left_of(size).rectangle_area_on_screen


def left_screen_area() -> RectangleAreaOnScreen:
    size = screen_size() / WidthScaling(2)
    return ORIGIN.as_top_left_of(size).rectangle_area_on_screen


def right_screen_area() -> RectangleAreaOnScreen:
    return left_screen_area() + screen_size().width / 2


def top_screen_area() -> RectangleAreaOnScreen:
    size = screen_size() / HeightScaling(2)
    return ORIGIN.as_top_left_of(size).rectangle_area_on_screen


def bottom_screen_area() -> RectangleAreaOnScreen:
    return top_screen_area() + screen_size().height / 2


def top_left_screen_area() -> RectangleAreaOnScreen:
    size = screen_size() / WidthAndHeightScaling(2)
    return ORIGIN.as_top_left_of(size).rectangle_area_on_screen


def top_right_screen_area() -> RectangleAreaOnScreen:
    return top_left_screen_area() + screen_size().width / 2


def bottom_left_screen_area() -> RectangleAreaOnScreen:
    return top_left_screen_area() + screen_size().height / 2


def bottom_right_screen_area() -> RectangleAreaOnScreen:
    return top_right_screen_area() + screen_size().height / 2
