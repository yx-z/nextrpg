from example.component.title import title
from nextrpg import Scene, TransitionScene, ViewOnlyScene


def entry_scene() -> Scene:
    return TransitionScene(title, from_scene=ViewOnlyScene)
