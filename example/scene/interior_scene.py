from dataclasses import dataclass
from functools import cached_property
from typing import Literal, Self, override

from example.scene.character import create_character_drawing
from example.scene.scene_common import (
    AUDIO_DIR,
    TMX_DIR,
    alert_sound,
)
from nextrpg import (
    DISMISS_EVENT,
    AvatarPosition,
    Color,
    EventfulScene,
    EventSpec,
    GameState,
    Height,
    LoadFromSave,
    MapMove,
    MapSpec,
    MusicSpec,
    NpcEventStartMode,
    NpcOnScreen,
    NpcSpec,
    PlayerOnScreen,
    PlayerSpec,
    Text,
    config,
    cutscene,
)


def interior_scene(player: PlayerSpec, state: GameState) -> MapSpec:
    # Local import to avoid circular dependency.
    from example.scene.exterior_scene import exterior_scene

    return MapSpec(
        tmx=TMX_DIR / "interior.tmx",
        player=player,
        move=MapMove("from_interior", "to_exterior", exterior_scene),
        npc=(
            greet_npc("$PixelFantasy_2-Priscilla.png", "Priscilla"),
            greet_npc("$PixelFantasy_3-Gale.png", "Gale"),
            NpcSpec(
                unique_name="Auto",
                event=EventSpec(enter_room, NpcEventStartMode.COLLIDE),
            ),
        ),
        music=MusicSpec(AUDIO_DIR / "bgm1.mp3"),
    )


def greet_npc(file: str, name: str) -> NpcSpec:
    return NpcSpec(
        unique_name=name,
        character_drawing=create_character_drawing(file),
        event=StatefulGreet(),
    )


def enter_room(
    player: PlayerOnScreen,
    npc: NpcOnScreen,
    scene: EventfulScene,
    state: GameState,
) -> Literal[DISMISS_EVENT]:
    # Load and play a sound.
    alert_sound().play()

    # A message on screen.
    scene: "You've entered this room!"
    # Testing Chinese characters.
    scene: "中文测试!"

    # Don't trigger the event again.
    return DISMISS_EVENT


@dataclass
class StatefulGreet(LoadFromSave[int]):
    """
    An example of how to persist state across NPC events & game save.
    """

    count: int = 1

    @override
    @cached_property
    def save_data_this_class(self) -> int:
        return self.count

    @override
    @classmethod
    def load_this_class_from_save(cls, data: int) -> Self:
        return cls(data)

    # Decorator to add a widescreen/cutscene effect when the event is triggered.
    @cutscene
    def __call__(
        self,
        player: PlayerOnScreen,
        npc: NpcOnScreen,
        scene: EventfulScene,
        state: GameState,
    ) -> Self:
        cfg = config().event.say_event.text_config
        # Customized text color/font config.
        # fmt: off
        scene["Interior Scene"]: Text("Greetings!", cfg.with_font_size(Height(40))) + Text(
        """This is...
        a sample """, cfg) + Text("nextrpg event", cfg.with_color(Color(128, 0, 255)))
        # fmt: on

        npc: "Nice to meet you! What's your name?"
        # Supply arguments via brackets.
        player[AvatarPosition.RIGHT]: f"Hello {npc.name}! I am {player.name}."
        npc: f"Hi! We've met {self.count} time(s)!"

        # State change.
        self.count += 1
