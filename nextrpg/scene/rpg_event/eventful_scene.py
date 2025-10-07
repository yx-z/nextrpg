from abc import abstractmethod
from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Any, Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npc_on_screen import NpcOnScreen
from nextrpg.character.npc_spec import NpcEventStartMode
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.core.dataclass_with_default import (
    private_init_below,
)
from nextrpg.core.log import Log
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.event.background_event import (
    BackgroundEvent,
    BackgroundEventSentinel,
)
from nextrpg.event.event_as_attr import EventAsAttr
from nextrpg.event.io_event import IoEvent, KeyboardKey, KeyPressDown
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.scene.scene import Scene

if TYPE_CHECKING:
    from nextrpg.scene.rpg_event.rpg_event_scene import EventGenerator

log = Log()


@dataclass(frozen=True)
class EventfulScene(EventAsAttr, Scene):
    player: PlayerOnScreen
    npcs: tuple[NpcOnScreen, ...]
    _: KW_ONLY = private_init_below()
    _started_npc: NpcOnScreen | None = None
    _ended_npc: NpcOnScreen | None = None
    _event: EventGenerator | None = None
    _event_result: Any = None
    _background_events: tuple[BackgroundEvent, ...] = ()

    def get_character(self, unique_name: str) -> CharacterOnScreen:
        if unique_name == self.player.spec.unique_name:
            return self.player
        return self._npc_dict[unique_name]

    def event(self, event: IoEvent) -> Self:
        player = self.player.event(event)
        if (
            not self._started_npc
            and isinstance(event, KeyPressDown)
            and event.key is KeyboardKey.CONFIRM
            and (npc := self._collided_npc)
            and npc.restart_event
            and (npc_event := npc.spec.event)
            and npc_event.start_mode is NpcEventStartMode.CONFIRM
        ):
            return replace(self, player=player, _started_npc=npc)
        return replace(self, player=player)

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        if next_event_scene := self._next_event(time_delta):
            return next_event_scene

        if self._started_npc:
            return self._start_event(self._started_npc, time_delta)

        if (
            (npc := self._collided_npc)
            and npc.restart_event
            and (not self._ended_npc or not self._ended_npc.is_same_name(npc))
            and (event := npc.spec.event)
            and event.start_mode is NpcEventStartMode.COLLIDE
        ):
            return self._start_event(npc, time_delta)

        return self.tick_without_event(time_delta)

    def tick_without_event(self, time_delta: Millisecond) -> Self:
        player = self.player.tick(time_delta, self.npcs)
        npcs = tuple(n.tick(time_delta, self._others(n)) for n in self.npcs)

        if self._collided_npc:
            ended_npc = self._ended_npc
        else:
            ended_npc = None

        ticked = replace(self, player=player, npcs=npcs, _ended_npc=ended_npc)

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

    @property
    def drawing_on_screens_shift(self) -> Coordinate | None:
        return None

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        background_events_drawing_on_screens = tuple(
            d for c in self._background_events for d in c.drawing_on_screens
        )
        if shift := self.drawing_on_screens_shift:
            drawing_on_screens = tuple(
                d.add_fast(shift) for d in self.drawing_on_screens_before_shift
            )
            return drawing_on_screens + background_events_drawing_on_screens
        return background_events_drawing_on_screens

    @property
    @abstractmethod
    def drawing_on_screens_before_shift(
        self,
    ) -> tuple[DrawingOnScreen, ...]: ...

    def is_complete(
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

    def _others(self, npc: NpcOnScreen) -> tuple[NpcOnScreen, ...]:
        return (self.player,) + tuple(n for n in self.npcs if n is not npc)

    @cached_property
    def _npc_dict(self) -> dict[str, NpcOnScreen]:
        return {n.spec.unique_name: n for n in self.npcs}

    @cached_property
    def _collided_npc(self) -> NpcOnScreen | None:
        for npc in self.npcs:
            if npc.collide_start_event(self.player):
                return npc
        return None

    def _start_event(self, npc: NpcOnScreen, time_delta: Millisecond) -> Self:
        started_npc = npc.start_event(self.player)
        npcs = tuple(
            started_npc if n.is_same_name(npc) else n for n in self.npcs
        )
        player = self.player.start_event(started_npc)
        ticked = replace(
            self, player=player, npcs=npcs, _started_npc=started_npc
        ).tick_without_event(time_delta)

        event = npc.spec.event.generator(
            ticked.player, ticked._started_npc, ticked
        )
        log.debug(t"Event {event} with {npc.spec.unique_name} started.")
        try:
            event_callable = next(event)
            return event_callable(event, ticked)
        except StopIteration as res:
            return ticked._complete_event(ticked, res.value)

    def _next_event(self, time_delta: Millisecond) -> Scene | None:
        if not self._event:
            return None

        ticked = self.tick_without_event(time_delta)
        try:
            create_next_scene = ticked._event.send(self._event_result)
            return create_next_scene(ticked._event, ticked)
        except StopIteration as res:
            return self._complete_event(ticked, res.value)

    def _complete_event(self, ticked: Self, restart_event: bool | None) -> Self:
        npc = ticked._started_npc.complete_event
        if restart_event is False:
            npc = replace(npc, restart_event=False)

        player = ticked.player.complete_event
        npcs = tuple(
            (npc if n.is_same_name(npc) else n.complete_event)
            for n in ticked.npcs
        )
        log.debug(
            t"Event {ticked._event} with {npc.spec.unique_name} completed."
        )
        return replace(
            self,
            player=player,
            npcs=npcs,
            _ended_npc=npc,
            _started_npc=None,
            _event=None,
            _event_result=None,
        )
