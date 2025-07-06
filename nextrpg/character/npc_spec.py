from dataclasses import dataclass, field

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.moving_npc_on_screen import MovingNpcOnScreen
from nextrpg.character.npcs import NpcOnScreen, RpgEventSpec
from nextrpg.config import config
from nextrpg.core import Millisecond, PixelPerMillisecond
from nextrpg.draw_on_screen import Coordinate, Polygon


@dataclass
class NpcSpec:
    """
    Base class to define NPC specifications.

    Arguments:
        `name`: Name of the NPC.

        `drawing`: Character drawing for the NPC.

        `event_spec`: Event specification for player/NPC interactions.
    """

    name: str
    character: CharacterDrawing
    event_spec: RpgEventSpec

    def put_on_screen(self, coord: Coordinate) -> NpcOnScreen:
        """
        Put the NPC on screen.

        Arguments:
            `coord`: The coordinate of the NPC on screen.

        Returns:
            `NpcOnScreen`: The NPC on screen.
        """
        return NpcOnScreen(
            coordinate=coord,
            character=self.character,
            event_spec=self.event_spec,
            name=self.name,
        )


@dataclass
class MovingNpcSpec(NpcSpec):
    """
    Moving NPC specification.

    Arguments:
        `move_speed`: Movement speed of the NPC in pixels per millisecond.

        `idle_duration`: Duration of the idle state.

        `move_duration`: Duration of the moving state.

        `observe_collisions`: Whether to observe collisions with the map.
    """

    move_speed: PixelPerMillisecond = field(
        default_factory=lambda: config().character.move_speed
    )
    idle_duration: Millisecond = field(
        default_factory=lambda: config().character.idle_duration
    )
    move_duration: Millisecond = field(
        default_factory=lambda: config().character.move_duration
    )
    observe_collisions: bool = True

    def put_moving_on_screen(
        self, coord: Coordinate, path: Polygon, collisions: list[Polygon]
    ) -> MovingNpcOnScreen:
        """
        Put the moving npc on screen.

        Arguments:
            `coord`: NPC initial coordinate.

            `path`: NPC moving path.

            `collisions`: NPC collision polygons.

        Returns:
            `MovingNpcOnScreen`: The moving npc on screen.
        """
        return MovingNpcOnScreen(
            character=self.character,
            coordinate=coord,
            collisions=collisions,
            move_speed=self.move_speed,
            name=self.name,
            event_spec=self.event_spec,
            path=path,
            idle_duration=self.idle_duration,
            move_duration=self.move_duration,
        )
