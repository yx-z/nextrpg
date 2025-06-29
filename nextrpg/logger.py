_debug_logs: list[str] = []


def debug_log(s: str) -> None:
    """
    Put a line of debug log on screen.

    Arguments:
        `s`: str to print on screen.

    Returns:
        `None`.
    """
    _debug_logs.append(s)


def get_debug_logs() -> list[str]:
    """
    Get current debug logs that aren't printed.

    Returns:
        `list[str]`: list of debug logs.
    """
    return _debug_logs


def clear_debug_logs() -> None:
    """
    Clear debug logs.

    Returns:
        `None`.
    """
    _debug_logs.clear()
