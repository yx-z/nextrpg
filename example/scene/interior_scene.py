from dataclasses import dataclass, replace
from functools import cached_property
from typing import Literal, Self, override

from example.scene.character import create_character_drawing
from example.scene.scene_common import SOUND_DIR, TMX_DIR, bgm_config, sound
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
    MapScene,
    NpcEventStartMode,
    NpcOnScreen,
    NpcSpec,
    PlayerOnScreen,
    PlayerSpec,
    Sound,
    Text,
    config,
    cutscene,
)


def interior_scene(player: PlayerSpec, state: GameState) -> MapScene:
    enter_room_spec = EventSpec(enter_room, NpcEventStartMode.COLLIDE)
    auto = NpcSpec(unique_name="Auto", event=enter_room_spec)

    # Local import to avoid circular dependency.
    from example.scene.exterior_scene import exterior_scene

    tmx = TMX_DIR / "interior.tmx"
    move = MapMove("from_interior", "to_exterior", exterior_scene)
    priscilla = create_npc("$PixelFantasy_2-Priscilla.png", "Priscilla")
    gale = create_npc("$PixelFantasy_3-Gale.png", "Gale")
    npc_specs = (priscilla, gale, auto)
    return MapScene(
        tmx=tmx,
        player_spec=player,
        move=move,
        npc_specs=npc_specs,
        sound=bgm(),
    )


def bgm() -> Sound:
    return Sound(SOUND_DIR / "bgm1.mp3", loop=True, config=bgm_config())


def create_npc(file: str, name: str) -> NpcSpec:
    character = create_character_drawing(file)
    greet = StatefulGreet()
    return NpcSpec(unique_name=name, character_drawing=character, event=greet)


def enter_room(
    player: PlayerOnScreen,
    npc: NpcOnScreen,
    scene: EventfulScene,
    state: GameState,
) -> Literal[DISMISS_EVENT]:
    sound().play()
    scene: "You've entered this room!"
    return DISMISS_EVENT


@dataclass(frozen=True)
class StatefulGreet(LoadFromSave[int]):
    count: int = 1

    @override
    @cached_property
    def save_data_this_class(self) -> int:
        return self.count

    @override
    @classmethod
    def load_this_class_from_save(cls, data: int) -> Self:
        return cls(data)

    @cutscene
    def __call__(
        self,
        player: PlayerOnScreen,
        npc: NpcOnScreen,
        scene: EventfulScene,
        state: GameState,
    ) -> Self:
        cfg = config().event.say_event.text_config
        # fmt: off
        scene["Interior Scene"]: Text("Greetings!", cfg.with_size(Height(40))) + Text(
        """This is...
        a sample """, cfg) + Text("nextrpg event", cfg.with_color(Color(128, 0, 255)))
        # fmt: on

        npc: "Nice to meet you! What's your name?"
        player[AvatarPosition.RIGHT]: f"Hello {npc.name}! I am {player.name}."
        npc: f"Hi! We've met {self.count} time(s)!"
        return replace(self, count=self.count + 1)
