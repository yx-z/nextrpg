from collections.abc import Callable
from functools import wraps
from types import FunctionType

from nextrpg.core.coordinate import Coordinate, ORIGIN
from nextrpg.core.dimension import Size
from nextrpg.draw.draw import RectangleOnScreen
from nextrpg.global_config.cutscene_config import CutsceneConfig
from nextrpg.global_config.global_config import config
from nextrpg.gui.area import gui_size
from nextrpg.scene.rpg_event.eventful_scene import EventGenerator
from nextrpg.scene.rpg_event.fade_in_scene import fade_in
from nextrpg.scene.rpg_event.fade_out_scene import fade_out


def cutscene[R, **P](
    arg: CutsceneConfig | Callable[P, R],
) -> (
    Callable[[Callable[P, R]], Callable[P, EventGenerator]]
    | Callable[P, EventGenerator]
):
    if isinstance(arg, CutsceneConfig):
        return lambda f: _cutscene(arg, f)
    return _cutscene(config().cutscene, arg)


def _cutscene[R, **P](
    cfg: CutsceneConfig, fun: Callable[P, R]
) -> Callable[P, EventGenerator]:
    def decorated(*args: P.args, **kwargs: P.kwargs) -> EventGenerator:
        gui_width, gui_height = gui_size()
        rect_height = gui_height * cfg.screen_height_percentage
        size = Size(gui_width, rect_height)
        top_border = RectangleOnScreen(ORIGIN, size)
        bottom_coord = Coordinate(0, gui_height - rect_height)
        bottom_border = RectangleOnScreen(bottom_coord, size)
        borders = tuple(
            r.fill(cfg.background) for r in (top_border, bottom_border)
        )

        sentinel = yield fade_in(borders, cfg.wait, cfg.duration)
        res = yield from fun(*args, **kwargs)
        yield fade_out(sentinel, cfg.wait, cfg.duration)
        return res

    decorate_with_global = FunctionType(
        decorated.__code__,
        fun.__globals__ | decorated.__globals__,
        fun.__name__,
        fun.__defaults__,
        (fun.__closure__ or ()) + (decorated.__closure__ or ()),
    )
    return wraps(fun)(decorate_with_global)
