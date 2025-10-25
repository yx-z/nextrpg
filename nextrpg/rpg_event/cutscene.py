from collections.abc import Callable
from functools import wraps
from types import FunctionType
from typing import Any, overload

from nextrpg.config.config import config
from nextrpg.config.rpg_event.cutscene_config import CutsceneConfig
from nextrpg.geometry.coordinate import ORIGIN
from nextrpg.gui.screen_area import screen_area, screen_size
from nextrpg.rpg_event.fade_in_event_scene import fade_in
from nextrpg.rpg_event.fade_out_event_scene import fade_out
from nextrpg.rpg_event.rpg_event_scene import EventGenerator


@overload
def cutscene[**P](
    arg: CutsceneConfig,
) -> Callable[[Callable[P, Any]], Callable[P, EventGenerator]]: ...


@overload
def cutscene[**P](arg: Callable[P, Any]) -> Callable[P, EventGenerator]: ...


def cutscene[**P](
    arg: CutsceneConfig | Callable[P, Any],
) -> (
    Callable[[Callable[P, Any]], Callable[P, EventGenerator]]
    | Callable[P, EventGenerator]
):
    if isinstance(arg, CutsceneConfig):
        return lambda f: _cutscene(arg, f)
    return _cutscene(config().cutscene, arg)


def _cutscene[**P](
    cfg: CutsceneConfig, fun: Callable[P, Any]
) -> Callable[P, EventGenerator]:
    def decorated(*args: P.args, **kwargs: P.kwargs) -> EventGenerator:
        size = screen_size() * cfg.cover_from_screen_scaling
        top_border = ORIGIN.as_top_left_of(size).rectangle_area_on_screen
        bottom_border = (
            screen_area()
            .bottom_left.as_top_left_of(size)
            .rectangle_area_on_screen
        )
        rectangle_area_on_screens = (top_border, bottom_border)
        borders = tuple(
            r.fill(cfg.background) for r in rectangle_area_on_screens
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
