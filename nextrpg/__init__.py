__version__ = "0.1.20"

from nextrpg.animation.abstract_animation import AbstractAnimation
from nextrpg.animation.abstract_animation_on_screen import (
    AbstractAnimationOnScreen,
)
from nextrpg.animation.animation_group import AnimationGroup
from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.animation.cycle import Cycle
from nextrpg.animation.cyclic_animation import CyclicAnimation
from nextrpg.animation.fade import Fade, FadeIn, FadeOut
from nextrpg.animation.move import Move, MoveFrom, MoveTo
from nextrpg.animation.scale import Scale, ScaleFrom, ScaleTo
from nextrpg.animation.sequence import Sequence
from nextrpg.animation.timed_animation_group import TimedAnimationGroup
from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.animation.timed_animation_spec import TimedAnimationSpec
from nextrpg.animation.typewriter import Typewriter
from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.character_spec import CharacterSpec
from nextrpg.character.moving_character_on_screen import MovingCharacterOnScreen
from nextrpg.character.moving_npc_on_screen import MovingNpcOnScreen
from nextrpg.character.npc_on_screen import NpcOnScreen, StrictNpcSpec
from nextrpg.character.npc_spec import (
    EventSpec,
    EventSpecParams,
    NpcEventStartMode,
    NpcSpec,
    RpgEvent,
    to_strict,
)
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.character.rpg_maker_character_drawing import (
    RpgMakerCharacterDrawing,
    RpgMakerCharacterDrawingDefaultFrameType,
    RpgMakerCharacterDrawingFrameType,
    RpgMakerCharacterDrawingXpFrameType,
    RpgMakerSpriteSheet,
)
from nextrpg.config.character.character_config import CharacterConfig
from nextrpg.config.character.rpg_maker_character_drawing_config import (
    RpgMakerCharacterDrawingConfig,
)
from nextrpg.config.config import (
    Config,
    config,
    initial_config,
    override_config,
    set_config,
)
from nextrpg.config.drawing.drawing_config import DrawingConfig
from nextrpg.config.drawing.text_config import TextConfig
from nextrpg.config.map_config import MapConfig
from nextrpg.config.menu_config import MenuConfig
from nextrpg.config.rpg_event.rpg_event_config import RpgEventConfig
from nextrpg.config.rpg_event.say_event_config import (
    AvatarPosition,
    SayEventColorBackgroundConfig,
    SayEventConfig,
    SayEventNineSliceBackgroundConfig,
)
from nextrpg.config.save_config import SaveConfig
from nextrpg.config.system.debug_config import DebugConfig
from nextrpg.config.system.game_loop_config import GameLoopConfig
from nextrpg.config.system.key_mapping_config import KeyCode, KeyMappingConfig
from nextrpg.config.system.window_config import WindowConfig
from nextrpg.config.timing_config import TimingConfig
from nextrpg.config.widget.button_config import ButtonConfig
from nextrpg.config.widget.widget_config import WidgetConfig
from nextrpg.core.cached_decorator import cached
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
    type_name,
)
from nextrpg.core.log import Log, LogEntry, MessageKeyAndDrawing, pop_messages
from nextrpg.core.metadata import HasMetadata
from nextrpg.core.save import (
    LoadFromSave,
    LoadFromSaveEnum,
    SaveData,
    SaveIo,
    UpdateFromSave,
    concat_save_key,
    module_and_class,
)
from nextrpg.core.time import Millisecond
from nextrpg.core.tmx_loader import TmxLoader, get_geometry
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.animation_on_screen_like import (
    AnimationOnScreenLike,
    animate,
    tick_optional,
)
from nextrpg.drawing.color import (
    BLACK,
    BLUE,
    GREEN,
    RED,
    TRANSPARENT,
    WHITE,
    Alpha,
    Color,
    alpha_from_percentage,
)
from nextrpg.drawing.drawing import Drawing, scale_surface
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.drawing_group_on_screen import DrawingGroupOnScreen
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.drawing.font import Font
from nextrpg.drawing.nine_slice import NineSlice
from nextrpg.drawing.polygon_drawing import PolygonDrawing
from nextrpg.drawing.polyline_drawing import PolylineDrawing
from nextrpg.drawing.rectangle_drawing import RectangleDrawing
from nextrpg.drawing.relative_animation_like import (
    RelativeAnimationLike,
    relative_animation_likes,
)
from nextrpg.drawing.sprite_sheet import SpriteSheet, SpriteSheetSelection
from nextrpg.drawing.text import Text
from nextrpg.drawing.text_group import TextGroup
from nextrpg.drawing.text_on_screen import TextOnScreen
from nextrpg.event.background_event import (
    BackgroundEvent,
    BackgroundEventSentinel,
)
from nextrpg.event.code_transformer import ADD_PARENT, ADD_YIELD, ANNOTATE_SAY
from nextrpg.event.event_as_attr import EventAsAttr
from nextrpg.event.event_transformer import (
    register_rpg_event,
    registered_rpg_events,
    transform,
)
from nextrpg.event.io_event import (
    IoEvent,
    KeyboardKey,
    KeyPressDown,
    KeyPressUp,
    Quit,
    WindowResize,
    is_key_press,
    quit,
    to_io_event,
)
from nextrpg.game.game import Game
from nextrpg.game.game_loop import GameLoop, last_scene
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import ORIGIN, Coordinate
from nextrpg.geometry.dimension import (
    ZERO_SIZE,
    Dimension,
    Height,
    HeightScaling,
    Pixel,
    PixelPerMillisecond,
    Size,
    Width,
    WidthAndHeightScaling,
    WidthScaling,
)
from nextrpg.geometry.direction import Direction, DirectionalOffset
from nextrpg.geometry.padding import (
    Padding,
    padding_for_all_sides,
    padding_for_both_sides,
)
from nextrpg.geometry.polygon_area_on_screen import (
    PolygonAreaOnScreen,
    get_bounding_rectangle_area_on_screen,
)
from nextrpg.geometry.polyline_on_screen import PolylineOnScreen
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.geometry.sizable import Sizable
from nextrpg.geometry.walk import Walk
from nextrpg.gui.screen_area import (
    bottom_left_screen_area,
    bottom_right_screen_area,
    bottom_screen_area,
    left_screen_area,
    right_screen_area,
    screen_area,
    screen_size,
    top_left_screen_area,
    top_right_screen_area,
    top_screen_area,
)
from nextrpg.gui.window import Window
from nextrpg.map.map_loader import MapLoader
from nextrpg.map.map_move import MapMove
from nextrpg.map.map_scene import MapScene, center_player
from nextrpg.rpg_event.cutscene import cutscene
from nextrpg.rpg_event.eventful_scene import EventfulScene
from nextrpg.rpg_event.fade_in_event_scene import (
    BackgroundFadeInEvent,
    FadeInEventScene,
    fade_in,
)
from nextrpg.rpg_event.fade_out_event_scene import (
    BackgroundFadeOutEvent,
    FadeOutEventScene,
    fade_out,
)
from nextrpg.rpg_event.rpg_event_scene import (
    EventCallable,
    EventGenerator,
    RpgEventScene,
    register_rpg_event_scene,
    registered_rpg_event_scenes,
)
from nextrpg.rpg_event.say_event.say_event_add_on import (
    SayEventAddOn,
    SayEventCharacterAddOn,
)
from nextrpg.rpg_event.say_event.say_event_scene import SayEventScene, say
from nextrpg.rpg_event.say_event.say_event_state import (
    SayEventFadeInState,
    SayEventFadeOutState,
    SayEventState,
    SayEventTypingState,
)
from nextrpg.scene.scene import Scene
from nextrpg.scene.transition_scene import TransitionScene
from nextrpg.widget.button import Button, ButtonOnScreen, DefaultButton
from nextrpg.widget.label import Label, LabelOnScreen
from nextrpg.widget.menu_scene import MenuScene
from nextrpg.widget.panel import Panel, PanelOnScreen
from nextrpg.widget.scroll_direction import ScrollDirection
from nextrpg.widget.sizable_widget import SizableWidget, SizableWidgetOnScreen
from nextrpg.widget.tmx_widget_group_on_screen import TmxWidgetGroupOnScreen
from nextrpg.widget.widget import Widget, WidgetOnScreen
from nextrpg.widget.widget_group import WidgetGroup, WidgetGroupOnScreen
