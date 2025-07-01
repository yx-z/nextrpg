from nextrpg.logger import clear_debug_logs, debug_log, get_debug_logs


def test_logger() -> None:
    debug_log("abc")
    assert "abc" in get_debug_logs()
    clear_debug_logs()
    assert not get_debug_logs()
