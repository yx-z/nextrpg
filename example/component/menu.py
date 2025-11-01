from collections.abc import Callable
from functools import cache
from pathlib import Path

from example.component.title import title
from nextrpg import (
    TRANSPARENT,
    Anchor,
    Button,
    ButtonConfig,
    ButtonOnScreen,
    DefaultButton,
    Direction,
    DirectionalOffset,
    DrawingOnScreens,
    FadeIn,
    GameSave,
    Height,
    MapScene,
    MoveTo,
    Padding,
    Panel,
    PanelOnScreen,
    SaveIo,
    ScrollDirection,
    Text,
    TextOnScreen,
    TimedAnimationSpec,
    TmxLoader,
    TransitionScene,
    WidgetGroup,
    WidgetOnScreen,
    Width,
)


@cache
def tmx() -> TmxLoader:
    tmx_path = Path("example/component/menu.tmx")
    return TmxLoader(tmx_path)


NUM_SAVE_SLOTS = 3


@cache
def menu_widget() -> WidgetGroup:
    WIDGET_OFFSET = DirectionalOffset(Direction.DOWN, 50)
    enter_animation = TimedAnimationSpec(FadeIn).compose(
        MoveTo, offset=WIDGET_OFFSET
    )
    save_slots = tuple(save_slot(i) for i in range(NUM_SAVE_SLOTS))
    save_panel = Panel(
        name="save_panel",
        children=save_slots,
        enter_animation=enter_animation,
    )
    save_button = DefaultButton(name="save", on_click=save_panel)

    title_scene = TransitionScene(title)
    title_button = DefaultButton(name="title", on_click=title_scene)

    widgets = (save_button, title_button)
    return WidgetGroup(
        children=widgets,
        scroll_direction=ScrollDirection.HORIZONTAL,
        enter_animation=enter_animation,
    )


PADDING_WIDTH = Width(10)
PADDING_HEIGHT = Height(10)


def save_slot(i: int) -> Callable[[PanelOnScreen], Button]:
    def create_button(panel: PanelOnScreen) -> Button:
        area = panel.area
        height = area.height / NUM_SAVE_SLOTS - PADDING_HEIGHT * 2
        width = area.width - PADDING_WIDTH * 2
        top_left = area.top_left + i * height + PADDING_HEIGHT + PADDING_WIDTH
        button = top_left.as_top_left_of(width * height)

        # To keep button size stable between idle and active.
        invisible_background = button.rectangle_area_on_screen.fill(TRANSPARENT)

        if game_save := SaveIo(str(i)).load(GameSave):
            save_slot_title = f"Save #{i + 1}: {game_save.save_time_str}"
        else:
            save_slot_title = f"Empty Save Slot #{i + 1}"
        text = Text(save_slot_title)
        text_on_screen = TextOnScreen(button.center, text, Anchor.CENTER)
        drawing_on_screens = DrawingOnScreens(
            (invisible_background, text_on_screen.drawing_on_screen)
        )
        return DefaultButton(
            text=drawing_on_screens.drawing_group_at_origin,
            coordinate=top_left,
            on_click=click_save(i),
            config=ButtonConfig(padding=Padding()),
        )

    return create_button


def click_save(i: int) -> Callable[[ButtonOnScreen], WidgetOnScreen]:
    def create_button(from_button: ButtonOnScreen) -> WidgetOnScreen:
        assert isinstance(map_scene := from_button.root, MapScene)
        game_save = GameSave(map_scene.creation_function)
        save_io = SaveIo(str(i))
        save_io.save(game_save)

        assert isinstance(panel := from_button.parent, PanelOnScreen)
        button = save_slot(i)(panel)
        button_on_screen = button.widget_on_screen(
            panel.name_to_on_screens, panel
        )
        return panel.replace(from_button, button_on_screen)

    return create_button
