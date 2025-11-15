from nextrpg.drawing.animation_on_screen_like import AnimationOnScreenLike
from nextrpg.event.io_event import IoEvent


class Scene(AnimationOnScreenLike):
    def event(self, event: IoEvent) -> Scene:
        return self
