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
from nextrpg.core.save import UpdateFromSave
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_on_screen_like import AnimationOnScreenLike
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.event.background_event import (
    BackgroundEvent,
    BackgroundEventSentinel,
)
from nextrpg.event.event_as_attr import EventAsAttr
from nextrpg.event.io_event import IoEvent, is_key_press
from nextrpg.event.rpg_event_scene import (
    DISMISS_EVENT,
    EventGenerator,
    RpgEventScene,
)
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.scene.scene import Scene
from nextrpg.sound.scene_with_sound import SceneWithSound

log = Log()


@dataclass(frozen=True, kw_only=True)
class EventfulScene(
    EventAsAttr, SceneWithSound, UpdateFromSave[dict[str, Any]]
):
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
        if (
            not self._started_npc
            and is_key_press(event, KeyMappingConfig.confirm)
            and (npc := self._collided_npc)
            and npc.restart_event
            and (spec := npc.spec.event_spec)
            and spec.start_mode is NpcEventStartMode.CONFIRM
        ):
            return self._start_event(npc, spec.generator, time_delta=None)
        player = self.player.event(event)
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
            and (not self._ended_npc or not self._ended_npc.has_same_name(npc))
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

        ticked_background_events = tuple(
            e
            for c in self._background_events
            if not (e := c.tick(time_delta)).is_complete
        )
        for background_event in ticked_background_events:
            ticked = background_event.apply(ticked)
        return replace(ticked, _background_events=ticked_background_events)

    @cached_property
    def drawing_on_screens_shift(self) -> Coordinate | None:
        return None

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        background_events_drawing_on_screens = tuple(
            d for c in self._background_events for d in c.drawing_on_screens
        )
        before_shift = DrawingOnScreens(self.drawing_on_screens_before_shift)
        drawing_on_screens = self.drawing_on_screens_after_shift(before_shift)
        return drawing_on_screens + background_events_drawing_on_screens

    @property
    @abstractmethod
    def drawing_on_screens_before_shift(
        self,
    ) -> tuple[DrawingOnScreen, ...]: ...

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

    @cached_property
    def npc_dict(self) -> dict[str, NpcOnScreen]:
        return {n.spec.unique_name: n for n in self.npcs}

    def drawing_on_screens_after_shift(
        self, animation_on_screen_like: AnimationOnScreenLike
    ) -> tuple[DrawingOnScreen, ...]:
        if self.drawing_on_screens_shift:
            return tuple(
                d + self.drawing_on_screens_shift
                for d in animation_on_screen_like.drawing_on_screens
            )
        return animation_on_screen_like.drawing_on_screens

    @override
    @cached_property
    def _save_data(self) -> dict[str, Any]:
        return {
            character.name: character.save_data
            for character in (self.player,) + self.npcs
        }

    @override
    def _update_from_save(self, data: dict[str, Any]) -> Self:
        player = self.player.update_from_save(data[self.player.name])
        npcs = tuple(npc.update_from_save(data[npc.name]) for npc in self.npcs)
        return replace(self, player=player, npcs=npcs)

    def _others(self, npc: NpcOnScreen) -> tuple[CharacterOnScreen, ...]:
        other_npcs = tuple(n for n in self.npcs if n is not npc)
        return (self.player,) + other_npcs

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
            started_npc if n.has_same_name(npc) else n for n in self.npcs
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
            return _complete_event(ticked, res.value)

    def _next_event(self, time_delta: Millisecond) -> Scene | None:
        if not self._event:
            return None
        ticked = self.tick_without_event(time_delta)
        try:
            create_next_scene = ticked._event.send(self._event_result)
            return create_next_scene(ticked._event, ticked)
        except StopIteration as res:
            return _complete_event(ticked, res.value)


def _complete_event[T: EventfulScene](
    ticked: T, event_spec: Any | Literal[DISMISS_EVENT] | None
) -> T:
    assert (
        npc := ticked._started_npc
    ), f"Expect _complete_event with a started_npc. Got {ticked}"
    npcs = tuple(
        _complete(n, event_spec) if n.has_same_name(npc) else n
        for n in ticked.npcs
    )
    assert (
        ticked._event
    ), f"Expect _complete_event with an ongoing _event. Got {ticked}"
    log.debug(t"Event {ticked._event} with {npc.spec.unique_name} completed.")
    return replace(
        ticked,
        player=ticked.player.complete_event,
        npcs=npcs,
        _ended_npc=npc,
        _started_npc=None,
        _event=None,
        _event_result=None,
    )


def _complete(
    npc: NpcOnScreen, event_spec: Any | Literal[DISMISS_EVENT] | None
) -> NpcOnScreen:
    npc = npc.complete_event
    if event_spec is DISMISS_EVENT:
        return replace(npc, restart_event=False)
    elif event_spec is not None:
        spec = npc.spec.with_event_spec(event_spec)
        return replace(npc, spec=spec)
    return npc
