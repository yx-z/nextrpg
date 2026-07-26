"""Tests for nextrpg.event.event_transformer.

Covers both the error path (source-less functions) and the happy path
(real functions with accessible source). The happy path exercises the
full transform pipeline: getsource → parse → AST transform → compile →
exec → return, which is the success branch of the try/except added for
robustness.
"""

import pytest

from nextrpg.event.event_transformer import (
    EventTransformError,
    transform_event,
)

# ---------------------------------------------------------------------------
# Module-level functions / classes with real source for the happy-path tests.
# inspect.getsource requires the definition to live in a .py file, so these
# cannot be lambdas or exec-defined.
# ---------------------------------------------------------------------------


def _simple_event():
    result = 1 + 2
    return result


class _SimpleCallable:
    """Callable class instance — exercises the non-function branch."""

    def __call__(self):
        return 42


def _event_with_closure():
    captured = 99

    def inner():
        return captured

    return inner


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


# ---------------------------------------------------------------------------
# Happy-path tests — exercise the full transform pipeline (lines 38-68).
# ---------------------------------------------------------------------------


def test_transform_event_success_returns_callable():
    """A normal function with accessible source is successfully transformed.

    This covers the success branch of the try/except: getsource + parse
    succeed, then the AST is transformed, compiled, and exec'd.
    """
    transformed = transform_event(_simple_event)
    assert callable(transformed)
    assert transformed() == 3


def test_transform_event_preserves_function_name():
    """The transformed function keeps the original name in the namespace."""
    transformed = transform_event(_simple_event)
    assert transformed.__name__ == "_simple_event"


def test_transform_event_callable_instance():
    """A callable class instance exercises the non-function branch.

    When ``fun`` is not a function (e.g. an instance with ``__call__``),
    the transformer reads the source of ``fun.__call__`` and returns a
    lambda that threads ``fun`` as the first argument (self).
    """
    obj = _SimpleCallable()
    transformed = transform_event(obj)
    assert callable(transformed)
    assert transformed() == 42


def test_transform_event_callable_instance_threads_self():
    """The returned lambda passes the original instance as ``self``."""
    obj = _SimpleCallable()
    transformed = transform_event(obj)
    # The lambda signature is (*args, **kwargs) → transformed(fun, *args, **kwargs)
    # Calling with no args passes fun as self.
    result = transformed()
    assert result == 42
