from dataclasses import dataclass

from nextrpg.config.event.cutscene_config import CutsceneConfig
from nextrpg.config.event.event_transformer_config import (
    EventTransformerConfig,
)
from nextrpg.config.event.say_event_config import SayEventConfig


@dataclass(frozen=True)
class RpgEventConfig:
    event_transformer: EventTransformerConfig = EventTransformerConfig()
    say_event: SayEventConfig = SayEventConfig()
    cutscene: CutsceneConfig = CutsceneConfig()
