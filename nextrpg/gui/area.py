from nextrpg.core.coordinate import ORIGIN
from nextrpg.core.dimension import (
    Height,
    HeightScaling,
    Size,
    Width,
    WidthAndHeightScaling,
    WidthScaling,
)
from nextrpg.draw.drawing import RectangleOnScreen
from nextrpg.global_config.global_config import config, initial_config
from nextrpg.global_config.window_config import ResizeMode


def gui_size() -> Size:
    match mode := config().window.resize:
        case ResizeMode.SCALE:
            return initial_config().window.size
        case ResizeMode.KEEP_NATIVE_SIZE:
            return config().window.size


def gui_width() -> Width:
    return gui_size().width


def gui_height() -> Height:
    return gui_size().height


def screen() -> RectangleOnScreen:
    return RectangleOnScreen(ORIGIN, gui_size())


def left_screen() -> RectangleOnScreen:
    return RectangleOnScreen(ORIGIN, gui_size() / WidthScaling(2))


def right_screen() -> RectangleOnScreen:
    return left_screen() + gui_size().width / 2


def top_screen() -> RectangleOnScreen:
    return RectangleOnScreen(ORIGIN, gui_size() / HeightScaling(2))


def bottom_screen() -> RectangleOnScreen:
    return top_screen() + gui_size().height / 2


def top_left_screen() -> RectangleOnScreen:
    return RectangleOnScreen(ORIGIN, gui_size() / WidthAndHeightScaling(2))


def top_right_screen() -> RectangleOnScreen:
    return top_left_screen() + gui_size().width / 2


def bottom_left_screen() -> RectangleOnScreen:
    return top_left_screen() + gui_size().height / 2


def bottom_right_screen() -> RectangleOnScreen:
    return top_right_screen() + gui_size().height / 2
