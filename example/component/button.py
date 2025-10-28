from typing import Callable

from nextrpg import (
    GREEN,
    WHITE,
    Button,
    Color,
    Coordinate,
    Cycle,
    DrawingGroup,
    DrawingOnScreen,
    FadeIn,
    FadeOut,
    Padding,
    Pixel,
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
    border_width: Pixel = 2,
    border_radius: Pixel = 5,
    background_alpha_percentage: float = 0.7,
    text_color: Color = GREEN,
    background_color: Color = WHITE,
    border_color: Color = WHITE,
) -> Button:
    text_config = config().text.colored(text_color)

    text = Text(name.capitalize(), text_config)
    background_border = text.drawings[0].background(
        background_color, padding, border_radius, border_width
    )
    background_fill = border_color.with_percentage_alpha(
        background_alpha_percentage
    )
    background = text.drawings[0].background(
        background_fill, padding, border_radius
    )

    fade_in = FadeIn((background_border, background))
    fade_out = FadeOut((background_border, background))
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
