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


def resolve_module_name(pkg_name: str) -> str:
    """Map a pip package name to the importable top-level module name.

    Resolution order:
    1. ``top_level.txt`` from distribution metadata
    2. Top-level ``__init__.py`` entries in ``dist.files``
    3. Top-level ``.py`` files (non-private) in ``dist.files``
    4. Fallback: ``pkg_name`` with hyphens replaced by underscores
    """
    try:
        dist = importlib.metadata.distribution(pkg_name)
        top_level = dist.read_text("top_level.txt")
        if top_level:
            first = next((ln for ln in top_level.splitlines() if ln.strip()), None)
            if first:
                return first.strip()
    except Exception:
        pass

    try:
        dist = importlib.metadata.distribution(pkg_name)
        if dist.files:
            for fp in dist.files:
                parts = fp.parts
                if len(parts) == 2 and parts[1] == "__init__.py":
                    return parts[0]
    except Exception:
        pass

    try:
        dist = importlib.metadata.distribution(pkg_name)
        if dist.files:
            for fp in dist.files:
                parts = fp.parts
                if (
                    len(parts) == 1
                    and fp.suffix == ".py"
                    and not fp.stem.startswith("_")
                ):
                    return fp.stem
    except Exception:
        pass

    return pkg_name.replace("-", "_")


def probe(pkg_name: str) -> dict[str, str | types.ModuleType | bool | None]:
    """Probe whether *pkg_name* is installed and importable.

    Returns a dict with keys ``pkg_name``, ``module_name``, ``module``,
    ``version``, and ``available``.  Never raises.
    """
    module_name = resolve_module_name(pkg_name)
    result: dict[str, str | types.ModuleType | bool | None] = {
        "pkg_name": pkg_name,
        "module_name": module_name,
        "module": None,
        "version": None,
        "available": False,
    }
    try:
        result["module"] = importlib.import_module(module_name)
        result["available"] = True
    except Exception:
        return result
    with contextlib.suppress(Exception):
        result["version"] = importlib.metadata.version(pkg_name)
    return result
