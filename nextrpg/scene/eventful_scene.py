from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from typing import Any, Self

from nextrpg import CharacterOnScreen
from nextrpg.character.npc_on_screen import NpcEventGenerator, NpcOnScreen
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.core.dataclass_with_instance_init import not_constructor_below
from nextrpg.core.logger import Logger
from nextrpg.core.time import Millisecond
from nextrpg.event.event_as_attr import EventAsAttr
from nextrpg.event.pygame_event import KeyboardKey, KeyPressDown, PygameEvent
from nextrpg.scene.scene import Scene

logger = Logger("RpgEventScene")


@dataclass(frozen=True)
class EventfulScene(EventAsAttr, Scene):
    player: PlayerOnScreen
    npcs: tuple[NpcOnScreen, ...]
    _: KW_ONLY = not_constructor_below()
    started_npc: NpcOnScreen | None = None
    _event_generator: NpcEventGenerator | None = None
    _event_result: Any = None

    def get_character(self, object_name: str) -> CharacterOnScreen:
        if object_name == self.player.spec.object_name:
            return self.player
        return self._npc_dict[object_name]

    def event(self, event: PygameEvent) -> Scene:
        if (
            self.started_npc
            or not isinstance(event, KeyPressDown)
            or event.key is not KeyboardKey.CONFIRM
            or not (npc := self._collided_npc)
            or not npc.spec.event
        ):
            return replace(self, player=self.player.event(event))

        logger.debug(t"Collided with {npc.spec.object_name}")
        started_scene = self._start_event(npc)
        generator = npc.spec.generator(
            started_scene.player, started_scene.started_npc, started_scene
        )
        logger.debug(t"Event {generator.__name__} started.")
        return next(generator)(generator, started_scene)

    def tick(self, time_delta: Millisecond) -> Scene:
        if next_event_scene := self._next_event(time_delta):
            return next_event_scene
        return self.tick_without_event(time_delta)

    def tick_without_event(self, time_delta: Millisecond) -> Self:
        player = self.player.tick(time_delta, self.npcs)
        npcs = tuple(n.tick(time_delta, self._others(n)) for n in self.npcs)
        return replace(self, player=player, npcs=npcs)

    def send(self, event: NpcEventGenerator, result: Any = None) -> Self:
        return replace(self, _event_generator=event, _event_result=result)

    def _others(self, npc: NpcOnScreen) -> tuple[NpcOnScreen, ...]:
        return (self.player,) + tuple(n for n in self.npcs if n is not npc)

    @cached_property
    def _npc_dict(self) -> dict[str, NpcOnScreen]:
        return {n.spec.object_name: n for n in self.npcs}

    @cached_property
    def _collided_npc(self) -> NpcOnScreen | None:
        for npc in self.npcs:
            if npc.start_event_rectangle.collide(
                self.player.start_event_rectangle
            ):
                return npc
        return None

    def _start_event(self, npc: NpcOnScreen) -> Self:
        started_npc = npc.start_event(self.player)
        npcs = tuple(
            started_npc if n.spec.object_name == npc.spec.object_name else n
            for n in self.npcs
        )
        return replace(
            self,
            player=self.player.start_event(started_npc),
            started_npc=started_npc,
            npcs=npcs,
        )

    def _next_event(self, time_delta: Millisecond) -> Scene | None:
        if not self._event_generator:
            return None

        ticked = self.tick_without_event(time_delta)
        try:
            create_next_scene = self._event_generator.send(self._event_result)
            return create_next_scene(self._event_generator, ticked)
        except StopIteration:
            logger.debug(t"Event {self._event_generator.__name__} completed.")
            return replace(
                self,
                player=ticked.player.complete_event,
                npcs=ticked._completed_npcs,
                started_npc=None,
                _event_generator=None,
                _event_result=None,
            )

    @cached_property
    def _completed_npcs(self) -> tuple[NpcOnScreen, ...]:
        return tuple(n.complete_event for n in self.npcs)
