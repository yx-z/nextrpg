_debug_logs: list[str] = []


def debug_log(s: str) -> None:
    _debug_logs.append(s)


def get_debug_logs() -> list[str]:
    return _debug_logs


def reset_debug_logs() -> None:
    _debug_logs.clear()
