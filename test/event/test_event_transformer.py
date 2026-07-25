"""Tests for nextrpg.event.event_transformer error handling.

The dialogue DSL rewrites function source via getsource/parse/exec. When source
is unavailable (REPL/eval/exec-defined, or source-less deployments) it must
raise a clear, actionable EventTransformError rather than an opaque
OSError/TypeError.

Note: a lambda defined in a .py file still has retrievable source, so to exercise
the source-less path we compile a function against a fake filename that
inspect.getsource cannot resolve.
"""

import pytest

from nextrpg.event.event_transformer import (
    EventTransformError,
    transform_event,
)


def _make_sourceless_function():
    code = compile("def f():\n    pass\n", "<no-source>", "exec")
    namespace: dict = {}
    exec(code, namespace)
    return namespace["f"]


def test_transform_event_raises_clear_error_when_source_unavailable():
    fun = _make_sourceless_function()
    with pytest.raises(EventTransformError) as exc_info:
        transform_event(fun)

    msg = str(exc_info.value).lower()
    assert "source" in msg, "error message should mention source"
    # Should point the user at a remedy.
    assert "defined in a" in msg or "non-macro" in msg
    # The original OSError must be chained as __cause__ for debugging.
    assert isinstance(
        exc_info.value.__cause__, OSError | TypeError | ValueError
    )


def test_transform_event_error_references_offending_function():
    fun = _make_sourceless_function()
    with pytest.raises(EventTransformError) as exc_info:
        transform_event(fun)
    # The offending callable should be referenced in the message.
    assert "<function f" in str(exc_info.value)
