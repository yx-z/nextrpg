from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.core.coordinate import ORIGIN, Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.time import Millisecond
from nextrpg.draw.animation import Animation
from nextrpg.draw.animation_on_screen import AnimationOnScreen
from nextrpg.draw.drawing import Drawing, DrawingOnScreen
from nextrpg.draw.drawing_group import DrawingGroup


@dataclass(frozen=True)
class RelativeAnimation:
    animation: Drawing | DrawingGroup | Animation | AnimationGroup
    shift: Size

    def tick(self, time_delta: Millisecond) -> Self:
        if isinstance(animation := self.animation, Animation | AnimationGroup):
            animation = animation.tick(time_delta)
        return replace(self, animation=animation)


@dataclass(frozen=True)
class AnimationGroup:
    relative_animations: tuple[RelativeAnimation, ...]

    def tick(self, time_delta: Millisecond) -> Self:
        relative_animations = tuple(
            relative_animation.tick(time_delta)
            for relative_animation in self.relative_animations
        )
        return replace(self, relative_animations=relative_animations)

    def drawing_on_screens(
        self, origin: Coordinate
    ) -> tuple[DrawingOnScreen, ...]:
        return AnimationGroupOnScreen(origin, self).drawing_on_screens

    def group_on_screen(self, origin: Coordinate) -> AnimationGroupOnScreen:
        return AnimationGroupOnScreen(origin, self)

    @cached_property
    def size(self) -> Size:
        return AnimationGroupOnScreen(ORIGIN, self).size

    @cached_property
    def top_left(self) -> Coordinate:
        return AnimationGroupOnScreen(ORIGIN, self).top_left


@dataclass(frozen=True)
class AnimationGroupOnScreen(AnimationOnScreen):
    origin: Coordinate
    animation_group: AnimationGroup

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        res: list[DrawingOnScreen] = []
        for relative, shift in self.animation_group.relative_animations:
            coordinate = self.origin + shift
            match relative:
                case Drawing() | Animation() as drawing_or_animation:
                    res.append(
                        drawing_or_animation.drawing_on_screen(coordinate)
                    )
                case DrawingGroup() | AnimationGroup() as group:
                    res += group.drawing_on_screens(coordinate)
        return tuple(res)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        animation_group = self.animation_group.tick(time_delta)
        return replace(self, animation_group=animation_group)

    def coordinate(
        self, arg: Drawing | DrawingGroup | Animation | AnimationGroup
    ) -> Coordinate | None:
        if arg == self.animation_group:
            return self.origin
        for relative, shift in self.animation_group.relative_animations:
            coordinate = self.origin + shift
            match relative:
                case Drawing() | Animation() as drawing_or_animation:
                    if arg == drawing_or_animation:
                        return coordinate
                case DrawingGroup() | AnimationGroup() as group:
                    if res := group.group_on_screen(coordinate).coordinate(arg):
                        return res
        return None
