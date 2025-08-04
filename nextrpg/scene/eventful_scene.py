from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from typing import Any, Callable, Generator, Self, TypeVar, override

from nextrpg import dataclass_with_instance_init
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npc_on_screen import NpcOnScreen
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.core.dataclass_with_instance_init import (
    instance_init,
    not_constructor_below,
)
from nextrpg.core.logger import Logger
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import DrawOnScreen
from nextrpg.event.event_as_attr import EventAsAttr
from nextrpg.event.pygame_event import KeyboardKey, KeyPressDown, PygameEvent
from nextrpg.scene.scene import Scene

logger = Logger()


@dataclass(frozen=True)
class EventfulScene(EventAsAttr, Scene):
    player: PlayerOnScreen
    npcs: tuple[NpcOnScreen, ...]
    _: KW_ONLY = not_constructor_below()
    started_npc: NpcOnScreen | None = None
    _event: EventGenerator | None = None
    _event_result: Any = None
    _background_events: tuple[BackgroundEvent, ...] = ()

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
        ticked = replace(self, player=player, npcs=npcs)

        ticked_background_events = tuple(
            c.tick(time_delta) for c in self._background_events
        )
        not_completed_background_events = tuple(
            c for c in ticked_background_events if not c.complete
        )
        for background_event in not_completed_background_events:
            ticked = background_event.apply(ticked)
        return replace(
            ticked, _background_events=not_completed_background_events
        )

    def complete(
        self,
        event: EventGenerator,
        event_result: Any = None,
        background_event: BackgroundEvent | None = None,
    ) -> Self:
        if background_event:
            background_events = self._background_events + (background_event,)
        else:
            background_events = self._background_events
        return replace(
            self,
            _event=event,
            _event_result=event_result,
            _background_events=background_events,
        )

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
        if not self._event:
            return None

        ticked = self.tick_without_event(time_delta)
        try:
            create_next_scene = self._event.send(self._event_result)
            return create_next_scene(self._event, ticked)
        except StopIteration:
            logger.debug(t"Event {self._event_generator.__name__} completed.")
            return replace(
                self,
                player=ticked.player.complete_event,
                npcs=ticked._completed_npcs,
                started_npc=None,
                _event=None,
                _event_result=None,
            )

    @cached_property
    def _completed_npcs(self) -> tuple[NpcOnScreen, ...]:
        return tuple(n.complete_event for n in self.npcs)

    @cached_property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        context_draws = tuple(
            d for c in self._background_events for d in c.draw_on_screens
        )
        return super().draw_on_screens + context_draws

    def get_background_event(
        self, sentinel: BackgroundEventSentinel
    ) -> BackgroundEvent:
        for background_event in self._background_events:
            if background_event.sentinel is sentinel:
                return background_event
        raise ValueError(f"No background event with sentinel {sentinel.cls}")

    def remove_background_event(
        self, sentinel: BackgroundEventSentinel
    ) -> Self:
        background_events = tuple(
            e for e in self._background_events if e.sentinel is not sentinel
        )
        return replace(self, _background_events=background_events)


@dataclass(frozen=True)
class BackgroundEventSentinel:
    cls: type


@dataclass_with_instance_init(frozen=True)
class BackgroundEvent(ABC):
    _: KW_ONLY = not_constructor_below()
    sentinel: BackgroundEventSentinel = instance_init(
        lambda self: BackgroundEventSentinel(type(self))
    )

    @property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        return ()

    def apply(self, scene: EventfulScene) -> EventfulScene:
        return scene

    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self: ...

    @property
    @abstractmethod
    def complete(self) -> bool: ...


@dataclass(frozen=True)
class RpgEventScene(Scene):
    generator: EventGenerator
    scene: EventfulScene

    @cached_property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        return self.scene.draw_on_screens + self.add_ons

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        ticked = replace(self, scene=self.scene.tick_without_event(time_delta))
        return self.post_tick(time_delta, ticked)

    def post_tick(self, time_delta: Millisecond, ticked: Self) -> Scene:
        return ticked

    @property
    def add_ons(self) -> tuple[DrawOnScreen, ...]:
        return ()


type EventCallable = Callable[[EventGenerator, EventfulScene], RpgEventScene]
type EventGenerator = Generator[EventCallable, Any, None]
