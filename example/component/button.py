from typing import Callable

from nextrpg import (
    GREEN,
    WHITE,
    Button,
    Coordinate,
    Cycle,
    DrawingGroup,
    DrawingOnScreen,
    FadeIn,
    FadeOut,
    Padding,
    Scene,
    Text,
    TimedAnimationOnScreens,
    Widget,
    config,
    padding_for_all_sides,
)


def button(
    name: str,
    on_click: Scene | Widget | Callable[[], None],
    padding: Padding = padding_for_all_sides(10),
    coordinate: Coordinate | None = None,
    enter_animation: (
        Callable[[tuple[DrawingOnScreen, ...]], TimedAnimationOnScreens] | None
    ) = None,
    exit_animation: (
        Callable[[tuple[DrawingOnScreen, ...]], TimedAnimationOnScreens] | None
    ) = None,
) -> Button:
    green = config().text.colored(GREEN)

    text = Text(name.capitalize(), green)
    border = text.drawings[0].background(
        WHITE, padding, width=1, border_radius=5
    )
    white = WHITE.with_percentage_alpha(0.7)
    background = text.drawings[0].background(white, padding, border_radius=5)

    fade_in = FadeIn((border, background))
    fade_out = FadeOut((border, background))
    animation = Cycle((fade_in, fade_out))
    active = DrawingGroup((animation, text.drawing))
    return Button(
        name=name,
        active=active,
        idle=text.drawing,
        on_click=on_click,
        coordinate=coordinate,
        enter_animation=enter_animation,
        exit_animation=exit_animation,
    )
