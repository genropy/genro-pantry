# Copyright (c) 2025 Softwell S.r.l. — MIT License
"""Resolve pip package names to importable modules and probe availability."""

import contextlib
import importlib
import importlib.metadata
import re
import types

try:
    from packaging.requirements import Requirement as _Requirement
except ImportError:  # pragma: no cover
    _Requirement = None  # type: ignore[assignment,misc]


def strip_specifier(raw_spec: str) -> str:
    """Extract the canonical package name from a PEP 508 dependency string.

    Uses ``packaging.requirements.Requirement`` when available, with a regex
    fallback for robustness.
    """
    if _Requirement is not None:
        try:
            return _Requirement(raw_spec).name
        except Exception:
            pass
    return re.split(r"[><=!;\[]", raw_spec)[0].strip()


def _get_distribution(pkg_name: str) -> importlib.metadata.Distribution | None:
    """Return the distribution for *pkg_name*, or ``None`` if not installed."""
    try:
        return importlib.metadata.distribution(pkg_name)
    except (importlib.metadata.PackageNotFoundError, ValueError):
        return None


def resolve_module_name(pkg_name: str, dist: importlib.metadata.Distribution | None = None) -> str:
    """Map a pip package name to the importable top-level module name.

    Resolution order:
    1. ``top_level.txt`` from distribution metadata
    2. Top-level ``__init__.py`` entries in ``dist.files``
    3. Top-level ``.py`` files (non-private) in ``dist.files``
    4. Fallback: ``pkg_name`` with hyphens replaced by underscores
    """
    if dist is None:
        dist = _get_distribution(pkg_name)
    if dist is None:
        return pkg_name.replace("-", "_")

    # Strategy 1: top_level.txt
    top_level = dist.read_text("top_level.txt")
    if top_level:
        first = next((ln for ln in top_level.splitlines() if ln.strip()), None)
        if first:
            return first.strip()

    # Strategy 2 & 3: dist.files
    if dist.files:
        for fp in dist.files:
            parts = fp.parts
            if len(parts) == 2 and parts[1] == "__init__.py":
                return parts[0]
        for fp in dist.files:
            parts = fp.parts
            if len(parts) == 1 and fp.suffix == ".py" and not fp.stem.startswith("_"):
                return fp.stem

    return pkg_name.replace("-", "_")


def probe(pkg_name: str) -> dict[str, str | types.ModuleType | bool | None]:
    """Probe whether *pkg_name* is installed (metadata only, no import).

    Returns a dict with keys ``pkg_name``, ``module_name``, ``module``,
    ``version``, and ``available``.

    The ``module`` field is ``None`` until :func:`load_module` is called.
    ``available`` is ``True`` if the distribution metadata was found.
    Never raises.
    """
    dist = _get_distribution(pkg_name)
    module_name = resolve_module_name(pkg_name, dist)
    version = None
    if dist is not None:
        with contextlib.suppress(Exception):
            version = dist.metadata["Version"]
    return {
        "pkg_name": pkg_name,
        "module_name": module_name,
        "module": None,
        "version": version,
        "available": dist is not None,
    }


def load_module(entry: dict) -> types.ModuleType | None:
    """Import the module for a probe entry. Returns the module or ``None``.

    Updates ``entry["module"]`` in place and sets ``available`` to ``False``
    if the import fails. Never raises.
    """
    if entry.get("module") is not None:
        return entry["module"]  # type: ignore[no-any-return]
    if not entry.get("available"):
        return None
    try:
        mod = importlib.import_module(entry["module_name"])
        entry["module"] = mod
        return mod
    except Exception:
        entry["available"] = False
        return None
