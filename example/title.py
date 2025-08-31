from pathlib import Path

from nextrpg import TitleScene


def title() -> TitleScene:
    return TitleScene(Path("example/asset/title.tmx"))
