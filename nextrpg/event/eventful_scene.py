from abc import abstractmethod
from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from typing import Any, Callable, Generator, Literal, Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npc_on_screen import NpcOnScreen
from nextrpg.character.npc_spec import NpcEventStartMode
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.config.system.key_mapping_config import KeyMappingConfig
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
from nextrpg.event.io_event import IoEvent, is_key_press
from nextrpg.event.rpg_event_scene import (
    DONT_RESTART_EVENT,
    EventGenerator,
    RpgEventScene,
)
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.scene.scene import Scene
from nextrpg.sound.scene_with_sound import SceneWithSound

log = Log()


@dataclass(frozen=True, kw_only=True)
class EventfulScene(EventAsAttr, SceneWithSound):
    player: PlayerOnScreen
    npcs: tuple[NpcOnScreen, ...] = ()
    _: KW_ONLY = private_init_below()
    _started_npc: NpcOnScreen | None = None
    _ended_npc: NpcOnScreen | None = None
    _event: EventGenerator | None = None
    _event_result: Any = None
    _background_events: tuple[BackgroundEvent, ...] = ()

    def get_character(self, unique_name: str) -> CharacterOnScreen:
        if unique_name == self.player.spec.unique_name:
            return self.player
        return self.npc_dict[unique_name]

    def event(self, event: IoEvent) -> Self:
        player = self.player.event(event)
        if (
            not self._started_npc
            and is_key_press(event, KeyMappingConfig.confirm)
            and (npc := self._collided_npc)
            and npc.restart_event
            and (spec := npc.spec.event_spec)
            and spec.start_mode is NpcEventStartMode.CONFIRM
        ):
            return self._start_event(npc, spec.generator, time_delta=None)
        return replace(self, player=player)

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        if next_event_scene := self._next_event(time_delta):
            return next_event_scene

        if self._started_npc and (spec := self._started_npc.spec.event_spec):
            return self._start_event(
                self._started_npc, spec.generator, time_delta
            )

        if (
            (npc := self._collided_npc)
            and npc.restart_event
            and (not self._ended_npc or not self._ended_npc.is_same_name(npc))
            and (spec := npc.spec.event_spec)
            and spec.start_mode is NpcEventStartMode.COLLIDE
        ):
            return self._start_event(npc, spec.generator, time_delta)

        return self.tick_without_event(time_delta)

    def tick_without_event(self, time_delta: Millisecond) -> Self:
        player = self.player.tick_with_others(time_delta, self.npcs)
        npcs = tuple(
            n.tick_with_others(time_delta, self._others(n)) for n in self.npcs
        )

        if self._collided_npc:
            ended_npc = self._ended_npc
        else:
            ended_npc = None

        base = super().tick(time_delta)
        ticked = replace(base, player=player, npcs=npcs, _ended_npc=ended_npc)

        ticked_background_events = [
            c.tick(time_delta) for c in self._background_events
        ]
        not_completed_background_events = [
            c for c in ticked_background_events if not c.is_complete
        ]
        for background_event in not_completed_background_events:
            ticked = background_event.apply(ticked)
        return replace(
            ticked, _background_events=not_completed_background_events
        )

    @cached_property
    def drawing_on_screens_shift(self) -> Coordinate | None:
        return None

    @override
    @cached_property
    def drawing_on_screens(self) -> list[DrawingOnScreen]:
        background_events_drawing_on_screens = [
            d for c in self._background_events for d in c.drawing_on_screens
        ]
        if shift := self.drawing_on_screens_shift:
            drawing_on_screens = [
                d + shift for d in self.drawing_on_screens_before_shift
            ]
            return drawing_on_screens + background_events_drawing_on_screens
        return background_events_drawing_on_screens

    @property
    @abstractmethod
    def drawing_on_screens_before_shift(
        self,
    ) -> list[DrawingOnScreen]: ...

    def complete(
        self,
        event: EventGenerator,
        event_result: Any = None,
        background_event: BackgroundEvent | None = None,
    ) -> Self:
        if background_event:
            background_events = self._background_events + [background_event]
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
        background_events = [
            e for e in self._background_events if e.sentinel is not sentinel
        ]
        return replace(self, _background_events=background_events)

    @cached_property
    def npc_dict(self) -> dict[str, NpcOnScreen]:
        return {n.spec.unique_name: n for n in self.npcs}

    def _others(self, npc: NpcOnScreen) -> list[CharacterOnScreen]:
        other_npcs = [n for n in self.npcs if n is not npc]
        return [self.player] + other_npcs

    @cached_property
    def _collided_npc(self) -> NpcOnScreen | None:
        for npc in self.npcs:
            if npc.collide_start_event(self.player):
                return npc
        return None

    def _start_event(
        self,
        npc: NpcOnScreen,
        event_generator: Callable[..., Generator[RpgEventScene, Any, None]],
        time_delta: Millisecond | None,
    ) -> Self:
        started_npc = npc.start_event(self.player)
        npcs = tuple(
            started_npc if n.is_same_name(npc) else n for n in self.npcs
        )
        player = self.player.start_event(started_npc)
        ticked = replace(
            self, player=player, npcs=npcs, _started_npc=started_npc
        )
        if time_delta:
            ticked = ticked.tick_without_event(time_delta)

        event = event_generator(ticked.player, ticked._started_npc, ticked)
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

    def _complete_event(
        self, ticked: Self, event_spec: Any | Literal[DONT_RESTART_EVENT] | None
    ) -> Self:
        assert (npc := ticked._started_npc)

        npc = npc.complete_event
        if event_spec is DONT_RESTART_EVENT:
            npc = replace(npc, restart_event=False)
        elif event_spec is not None:
            spec = npc.spec.with_event_spec(event_spec)
            npc = replace(npc, spec=spec)

        player = ticked.player.complete_event
        npcs = [
            (npc if n.is_same_name(npc) else n.complete_event)
            for n in ticked.npcs
        ]
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
