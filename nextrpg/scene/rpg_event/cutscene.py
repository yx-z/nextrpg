from collections.abc import Callable
from functools import wraps
from types import FunctionType

from nextrpg.config.config import config
from nextrpg.config.cutscene_config import CutsceneConfig
from nextrpg.geometry.coordinate import ORIGIN
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.gui.area import gui_height, gui_size
from nextrpg.scene.rpg_event.fade_in_scene import fade_in
from nextrpg.scene.rpg_event.fade_out_scene import fade_out
from nextrpg.scene.rpg_event.rpg_event_scene import EventGenerator


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
        size = gui_size() * cfg.cover_from_screen_scaling
        top_border = RectangleAreaOnScreen(ORIGIN, size)
        bottom_border = top_border + gui_height() - size.height
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
