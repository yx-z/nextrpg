from pygame.time import get_ticks

type Timepoint = int | float


def get_timepoint() -> Timepoint:
    return get_ticks()
