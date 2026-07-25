"""Guard the public API surface of `nextrpg`.

The top-level `nextrpg/__init__.py` hand-maintains an explicit import list and
auto-derives `__all__` from it. These tests ensure that contract stays
self-consistent (no dangling exports, no leaked subpackages, headline symbols
present) so the public API cannot silently drift.
"""

import inspect

import nextrpg

# A representative slice of the headline public API that users are most likely
# to import. If any of these disappears from the top-level package, something is
# wrong with the export list.
_HEADLINE_SYMBOLS = [
    "AnimationGroup",
    "AvatarPosition",
    "CharacterOnScreen",
    "Color",
    "Coordinate",
    "EventfulScene",
    "EventSpec",
    "GameState",
    "Height",
    "LoadFromSave",
    "MapMove",
    "MapSpec",
    "MusicSpec",
    "NpcOnScreen",
    "NpcSpec",
    "NpcEventStartMode",
    "PlayerOnScreen",
    "PlayerSpec",
    "Text",
    "config",
    "cutscene",
]


def test_all_is_defined_and_well_formed():
    assert hasattr(nextrpg, "__all__"), "nextrpg must define __all__"
    all_names = nextrpg.__all__
    assert isinstance(all_names, list), "__all__ must be a list"
    assert all_names, "__all__ must be non-empty"
    assert all(isinstance(n, str) for n in all_names)
    # No private/dunder names leak into the public surface.
    assert not any(n.startswith("_") for n in all_names), (
        "private names must not appear in __all__"
    )
    # Auto-derived from dir(), which is sorted, so __all__ must stay sorted.
    assert all_names == sorted(all_names), "__all__ must be sorted"


def test_no_dangling_or_module_exports():
    for name in nextrpg.__all__:
        assert hasattr(nextrpg, name), (
            f"{name!r} is in __all__ but missing from the nextrpg namespace "
            f"(dangling export)"
        )
        obj = getattr(nextrpg, name)
        # The public API is symbols (classes, functions, constants), not
        # subpackages. A submodule here would mean a leaked import.
        assert not inspect.ismodule(obj), (
            f"{name!r} is a module; subpackages must not be in __all__"
        )


def test_all_matches_public_namespace():
    # Every public (non-underscore) symbol that nextrpg actually exposes should
    # be listed in __all__, and vice versa. Subpackage attributes that Python
    # attaches to the package object are allowed in dir() but must not appear in
    # __all__.
    public_in_namespace = {
        n for n in dir(nextrpg) if not n.startswith("_")
    }
    exported = set(nextrpg.__all__)
    # __all__ must be a subset of the public namespace (nothing dangling).
    assert exported <= public_in_namespace
    # Every non-module public attribute sourced from nextrpg must be exported.
    not_exported = {
        n
        for n in public_in_namespace - exported
        if not inspect.ismodule(getattr(nextrpg, n))
        and getattr(getattr(nextrpg, n), "__module__", "").startswith("nextrpg")
    }
    assert not not_exported, (
        f"public nextrpg symbols not exported in __all__: {sorted(not_exported)}"
    )


def test_headline_symbols_exported():
    missing = [s for s in _HEADLINE_SYMBOLS if s not in nextrpg.__all__]
    assert not missing, f"headline symbols missing from __all__: {missing}"
