from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from typing import Any, Self

from nextrpg import CharacterOnScreen
from nextrpg.character.npc_on_screen import NpcOnScreen, RpgEventGenerator
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.core.dataclass_with_instance_init import not_constructor_below
from nextrpg.core.logger import Logger
from nextrpg.core.time import Millisecond
from nextrpg.event.event_as_attr import event_as_attr
from nextrpg.event.pygame_event import KeyboardKey, KeyPressDown, PygameEvent
from nextrpg.scene.scene import Scene

logger = Logger("RpgEventScene")


@dataclass(frozen=True)
@event_as_attr
class EventfulScene(Scene):
    """Scene that supports event execution via coroutines/generators.

    This scene type allows for complex event sequences to be executed
    using Python generators. It manages the state of ongoing events
    and provides methods for event continuation and completion.

    Attributes:
        player: The player character on screen.
        npcs: Tuple of NPCs present in the scene.
        npc: Currently active NPC (if any).
        _event_generator: Current event generator being executed.
        _event_result: Result from the previous event step.

    Example:
        ```python
        scene = EventfulScene(
            player=player,
            npcs=(npc1, npc2)
        )

        # Handle events
        scene = scene.event(key_press_event)

        # Update scene over time
        scene = scene.tick(time_delta)
        ```
    """

    player: PlayerOnScreen
    npcs: tuple[NpcOnScreen, ...]
    _: KW_ONLY = not_constructor_below()
    npc: NpcOnScreen | None = None
    _event_generator: RpgEventGenerator | None = None
    _event_result: Any = None

    def get_character(self, object_name: str) -> CharacterOnScreen:
        print(f"{self.player.spec.object_name=} {object_name=}")
        if object_name == self.player.spec.object_name:
            return self.player
        return self.get_npc(object_name)

    def get_npc(self, object_name: str) -> NpcOnScreen:
        return self._npc_dict[object_name]

    def event(self, event: PygameEvent) -> Scene:
        if (
            not self.npc
            and isinstance(event, KeyPressDown)
            and event.key is KeyboardKey.CONFIRM
            and (npc := self._collided_npc)
        ):
            logger.debug(t"Collided with {npc.spec.object_name}")
            scene = self._trigger(npc)
            generator = scene.npc.spec.generator(scene.player, scene.npc, scene)
            logger.debug(t"Event {generator.__name__} started.")
            return next(generator)(generator, scene)
        return replace(self, player=self.player.event(event))

    def tick(self, time_delta: Millisecond) -> Scene:
        if self._next_event:
            return self._next_event
        return self.tick_without_event(time_delta)

    def tick_without_event(self, time_delta: Millisecond) -> Self:
        """Update scene state without processing events.

        Args:
            time_delta: Time elapsed since last update in milliseconds.

        Returns:
            Updated scene with player and NPCs updated.
        """
        return replace(
            self,
            player=self.player.tick(time_delta),
            npcs=tuple(n.tick(time_delta) for n in self.npcs),
        )

    def send(self, event: RpgEventGenerator, result: Any = None) -> Self:
        """Continue event execution and optionally send the result of the current event.

        This method is used to continue the execution of an event generator
        and can pass a result value to the generator.

        Args:
            event: The generator to generate the next event.
            result: Result of the current event, passing to the generator.

        Returns:
            Scene that shall continue with the next event.
        """
        return replace(self, _event_generator=event, _event_result=result)

    @cached_property
    def _npc_dict(self) -> dict[str, NpcOnScreen]:
        return {n.spec.object_name: n for n in self.npcs}

    @cached_property
    def _collided_npc(self) -> NpcOnScreen | None:
        for npc in self.npcs:
            if npc.draw_on_screen.rectangle_on_screen.collide(
                self.player.draw_on_screen.rectangle_on_screen
            ):
                return npc
        return None

    def _trigger(self, npc: NpcOnScreen) -> Self:
        triggered_npc = npc.start_event(self.player)
        npcs = tuple(
            triggered_npc if n.spec.object_name == npc.spec.object_name else n
            for n in self.npcs
        )
        return replace(
            self,
            player=self.player.start_event(triggered_npc),
            npc=triggered_npc,
            npcs=npcs,
        )

    @cached_property
    def _next_event(self) -> Scene | None:
        if not self._event_generator:
            return None

        try:
            create_next_scene = self._event_generator.send(self._event_result)
            return create_next_scene(self._event_generator, self)
        except StopIteration:
            logger.debug(t"Event {self._event_generator.__name__} completed.")
            return replace(
                self,
                player=self.player.complete_event,
                npcs=self._completed_npcs,
                npc=None,
                _event_generator=None,
                _event_result=None,
            )

    @cached_property
    def _completed_npcs(self) -> tuple[NpcOnScreen, ...]:
        return tuple(n.complete_event for n in self.npcs)


@dataclass(frozen=True)
class RpgEventScene(Scene):
    """Scene wrapper for RPG events.

    This class represents a scene that is part of an RPG event sequence.
    It contains the event generator and the underlying scene context.

    Attributes:
        generator: The generator to continue after the event.
        scene: The scene to continue.

    Example:
        ```python
        event_scene = RpgEventScene(
            generator=event_generator,
            scene=base_scene
        )
        ```
    """

    generator: RpgEventGenerator
    scene: EventfulScene
