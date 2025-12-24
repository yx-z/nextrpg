import logging
from abc import abstractmethod
from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from typing import Any, Callable, Generator, Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npc_on_screen import NpcOnScreen, replace_npc
from nextrpg.character.npc_spec import EventSpecParams, NpcEventStartMode
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.config.system.key_mapping_config import KeyMappingConfig
from nextrpg.core.dataclass_with_default import (
    private_init_below,
)
from nextrpg.core.logger import Logger
from nextrpg.core.save import UpdateFromSave
from nextrpg.core.time import Millisecond
from nextrpg.core.util import generator_name
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import (
    DrawingOnScreens,
    drawing_on_screens,
)
from nextrpg.drawing.sprite_on_screen import SpriteOnScreen
from nextrpg.event.background_event import (
    BackgroundEvent,
    BackgroundEventSentinel,
)
from nextrpg.event.base_event import BaseEvent
from nextrpg.event.event_as_attr import EventAsAttr
from nextrpg.event.event_scene import (
    DISMISS_EVENT,
    EventCallable,
    EventCompletion,
    EventGenerator,
)
from nextrpg.event.io_event import is_key_press
from nextrpg.game.game_state import GameState
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.scene.scene import Scene

on_screen_logger = Logger("event")
console_logger = logging.getLogger("event")


@dataclass(frozen=True, kw_only=True)
class EventfulScene(EventAsAttr, Scene, UpdateFromSave[dict[str, Any]]):
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

    def event(
        self, event: BaseEvent, state: GameState
    ) -> tuple[Self, GameState]:
        if (
            not self._started_npc
            and is_key_press(event, KeyMappingConfig.confirm)
            and (npc := self._collided_npc)
            and npc.restart_event
            and (spec := npc.spec.event_spec)
            and spec.start_mode is NpcEventStartMode.CONFIRM
        ):
            return self._start_event(npc, spec.generator, state)
        player = self.player.event(event)
        with_player = replace(self, player=player)
        return with_player, state

    @override
    def tick(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Scene, GameState]:
        if next_event := self._next_event(time_delta, state):
            return next_event

        if self._started_npc and (spec := self._started_npc.spec.event_spec):
            return self._start_event(
                self._started_npc, spec.generator, state, time_delta
            )

        if (
            (npc := self._collided_npc)
            and npc.restart_event
            and (not self._ended_npc or not self._ended_npc.has_same_name(npc))
            and (spec := npc.spec.event_spec)
            and spec.start_mode is NpcEventStartMode.COLLIDE
        ):
            return self._start_event(npc, spec.generator, state, time_delta)
        return self.tick_without_event(time_delta, state)

    def tick_without_event(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Self, GameState]:
        player = self.player.tick_with_others(time_delta, self.npcs)
        npcs = tuple(
            n.tick_with_others(time_delta, self._others(n)) for n in self.npcs
        )

        if self._collided_npc:
            ended_npc = self._ended_npc
        else:
            ended_npc = None

        ticked = replace(self, player=player, npcs=npcs, _ended_npc=ended_npc)
        background_events: list[BackgroundEvent] = []
        for background_event in self._background_events:
            event, ticked, state = background_event.tick_with_state(
                time_delta, ticked, state
            )
            if not event.is_complete:
                background_events.append(event)
        scene = replace(ticked, _background_events=tuple(background_events))
        return scene, state

    @cached_property
    def drawing_on_screens_shift(self) -> Coordinate | None:
        return None

    @cached_property
    def drawing_on_screens(self) -> DrawingOnScreens:
        background_events_drawing_on_screens = drawing_on_screens(
            c.drawing_on_screens for c in self._background_events
        )
        return (
            self.drawing_on_screens_after_shift(
                self.drawing_on_screens_before_shift
            )
            + background_events_drawing_on_screens
        )

    @property
    @abstractmethod
    def drawing_on_screens_before_shift(
        self,
    ) -> DrawingOnScreens: ...

    def complete(
        self,
        event_result: Any | None = None,
        background_event: BackgroundEvent | None = None,
    ) -> Self:
        if background_event:
            background_events = self._background_events + (background_event,)
        else:
            background_events = self._background_events
        return replace(
            self,
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
        self, animation_on_screen_like: SpriteOnScreen
    ) -> DrawingOnScreens:
        if self.drawing_on_screens_shift:
            # Use raw coordinate value shift (instead of __add__) due to performance.
            top = self.drawing_on_screens_shift.top_value
            left = self.drawing_on_screens_shift.left_value
            return drawing_on_screens(
                DrawingOnScreen(
                    Coordinate(
                        d.top_left.left_value + left, d.top_left.top_value + top
                    ),
                    d.drawing,
                )
                for d in animation_on_screen_like.drawing_on_screens
            )
        return animation_on_screen_like.drawing_on_screens

    @override
    @cached_property
    def save_data_this_class(self) -> dict[str, Any]:
        return {
            character.name: character.save_data
            for character in (self.player,) + self.npcs
        }

    @override
    def update_this_class_from_save(self, data: dict[str, Any]) -> Self:
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
        event_creation_function: Callable[
            [*EventSpecParams],
            Generator[EventCallable, Any, None],
        ],
        state: GameState,
        time_delta: Millisecond | None = None,
    ) -> tuple[Self, GameState]:
        started_npc = npc.start_event(self.player)
        npcs = replace_npc(self.npcs, started_npc)
        player = self.player.start_event(started_npc)
        started = replace(
            self, player=player, npcs=npcs, _started_npc=started_npc
        )
        if time_delta:
            started, state = started.tick_without_event(time_delta, state)

        event_generator = event_creation_function(
            started.player, started._started_npc, started, state
        )
        event_callable = next(event_generator)
        on_screen_logger.debug(
            f"Event {generator_name(event_generator)} with {npc.name} started.",
            console_logger,
        )
        ticked_with_event = replace(started, _event=event_generator)
        event = event_callable(ticked_with_event)
        return event, state

    def _next_event(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Scene, GameState] | None:
        if not self._event:
            return None
        ticked, state = self.tick_without_event(time_delta, state)
        try:
            create_next_scene = ticked._event.send(self._event_result)
            next_scene = create_next_scene(ticked)
            return next_scene, state
        except StopIteration as res:
            completed = ticked._complete_event(res.value)
            return completed, state

    def _complete_event(self, event_completion: EventCompletion) -> Self:
        started_npc = self._started_npc
        assert (
            started_npc
        ), f"Expect _complete_event with a started_npc. Got {self}"
        npcs = tuple(
            (
                _complete(n, event_completion)
                if n.has_same_name(started_npc)
                else n
            )
            for n in self.npcs
        )
        assert (
            self._event
        ), f"Expect _complete_event with an ongoing _event. Got {self}"
        on_screen_logger.debug(
            f"Event {generator_name(self._event)} with {started_npc.name} completed."
        )
        return replace(
            self,
            player=self.player.complete_event,
            npcs=npcs,
            _ended_npc=started_npc,
            _started_npc=None,
            _event=None,
            _event_result=None,
        )


def _complete(
    npc: NpcOnScreen, event_completion: EventCompletion
) -> NpcOnScreen:
    npc = npc.complete_event
    if event_completion is DISMISS_EVENT:
        return replace(npc, restart_event=False)
    elif event_completion is not None:
        spec = npc.spec.with_event_spec(event_completion)
        return replace(npc, spec=spec)
    return npc
