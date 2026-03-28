# Copyright (c) 2025 Softwell S.r.l. — MIT License
"""Pantry — the capability registry."""

import functools
import importlib
import types
from collections.abc import Callable
from pathlib import Path

from ._discovery import find_pyproject, parse_optional_deps
from ._probe import probe, strip_specifier


class Pantry:
    """Runtime registry of optional-dependency availability.

    Build via the class methods :meth:`from_pyproject` or :meth:`discover`,
    or pass pre-built probe data directly.
    """

    _UNRESOLVED = object()

    def __init__(self, data: dict[str, dict], groups: dict[str, list[str]] | None = None):
        self._data = data
        self._groups = groups or {}
        self._lazy: dict[str, object] = {}

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def from_pyproject(cls, path: str | Path) -> "Pantry":
        """Parse *path* and probe every listed optional dependency."""
        path = Path(path)
        groups = parse_optional_deps(path)
        data: dict[str, dict] = {}
        pkg_to_groups: dict[str, list[str]] = {}
        for group, specs in groups.items():
            for raw in specs:
                name = strip_specifier(raw)
                if name not in data:
                    data[name] = probe(name)
                pkg_to_groups.setdefault(name, []).append(group)
        return cls(data, groups={g: [strip_specifier(s) for s in specs] for g, specs in groups.items()})

    @classmethod
    def discover(cls, start: Path | None = None) -> "Pantry":
        """Find ``pyproject.toml`` by walking upward, then probe all optional deps."""
        return cls.from_pyproject(find_pyproject(start))

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def has(self, *pkgs: str) -> bool:
        """Return ``True`` if all listed packages are available.

        Single package::

            pantry.has("pillow")

        Multiple packages (all must be available)::

            pantry.has("pillow", "numpy")
        """
        return all(
            (e := self._data.get(p)) is not None and bool(e.get("available"))
            for p in pkgs
        )

    def has_group(self, group: str) -> bool:
        """Return ``True`` if at least one package in *group* is available."""
        pkgs = self._groups.get(group, [])
        return any(self.has(p) for p in pkgs)

    _sentinel = object()

    def get(self, pkg: str, default: object = _sentinel) -> types.ModuleType | None:
        """Return the imported module for *pkg*.

        Without *default*, returns ``None`` when the package is unavailable.
        With *default*, returns *default* instead.
        """
        entry = self._data.get(pkg)
        if entry is None or not entry.get("available"):
            return None if default is self._sentinel else default  # type: ignore[return-value]
        return entry.get("module")  # type: ignore[return-value]

    def __getitem__(self, key: str) -> types.ModuleType:
        """Return a module (or lazy-resolved object) for *key*.

        Checks lazy imports first, then the pyproject.toml probe data.

        External dependencies::

            PIL = pantry["pillow"]

        Lazy-registered own modules::

            pantry.lazy_import("myapp.models.User")
            User = pantry["myapp.models.User"]
        """
        # Lazy imports (own modules) take priority
        if key in self._lazy:
            obj = self._lazy[key]
            if obj is self._UNRESOLVED:
                obj = self._resolve_lazy(key)
                self._lazy[key] = obj
            return obj  # type: ignore[return-value]

        # External dependencies from pyproject.toml
        mod = self.get(key)
        if mod is None:
            raise RuntimeError(
                f"Package '{key}' is not available. "
                f"Install with: pip install {key}"
            )
        return mod

    # ------------------------------------------------------------------
    # Lazy import (own modules — circular import breaker)
    # ------------------------------------------------------------------

    def lazy_import(self, *paths: str) -> None:
        """Register dotted paths for deferred import.

        Use this for your **own project modules** to break circular imports.
        The actual import happens on first ``pantry["path"]`` access.

        This is separate from the external dependency system (``has``, ``get``,
        ``report``). Those operate on pyproject.toml optional-dependencies.

        Example::

            pantry.lazy_import("myapp.models.User", "myapp.db.Session")

            # later, when all modules are loaded:
            User = pantry["myapp.models.User"]
        """
        for path in paths:
            if path not in self._lazy:
                self._lazy[path] = self._UNRESOLVED

    def _resolve_lazy(self, path: str) -> object:
        """Import and resolve a dotted path.

        Tries ``importlib.import_module(path)`` first (submodules).
        On failure, imports the parent and uses ``getattr`` (classes, functions).
        """
        try:
            return importlib.import_module(path)
        except ImportError:
            pass

        dot = path.rfind(".")
        if dot < 0:
            raise RuntimeError(f"Lazy import failed: no module named '{path}'")

        parent_path, attr_name = path[:dot], path[dot + 1:]
        try:
            parent = importlib.import_module(parent_path)
        except ImportError:
            raise RuntimeError(
                f"Lazy import failed: no module named '{parent_path}'"
            ) from None
        try:
            return getattr(parent, attr_name)
        except AttributeError:
            raise RuntimeError(
                f"Lazy import failed: '{parent_path}' has no attribute '{attr_name}'"
            ) from None

    # ------------------------------------------------------------------
    # Decorator
    # ------------------------------------------------------------------

    def __call__(self, *pkgs: str) -> Callable:
        """Decorator that guards a function behind one or more packages.

        Usage::

            @pantry("pillow", "numpy")
            def process(path):
                ...

        Raises ``RuntimeError`` at call-time when any required package is missing.
        """
        def decorator(fn: Callable) -> Callable:
            @functools.wraps(fn)
            def wrapper(*args: object, **kwargs: object) -> object:
                missing = [p for p in pkgs if not self.has(p)]
                if missing:
                    raise RuntimeError(
                        f"{fn.__qualname__} requires: {', '.join(missing)}. "
                        f"Install with: pip install {' '.join(missing)}"
                    )
                return fn(*args, **kwargs)
            return wrapper
        return decorator

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def report(self) -> str:
        """Return a formatted summary table of all probed packages."""
        lines: list[str] = []
        lines.append("pantry report")

        rows: list[tuple[str, str, str, str, str]] = []
        for group, pkgs in sorted(self._groups.items()):
            for pkg in pkgs:
                entry = self._data.get(pkg, {})
                module_name = str(entry.get("module_name", pkg))
                version = str(entry.get("version") or "-")
                ok = "\u2713" if entry.get("available") else "\u2717"
                rows.append((group, pkg, module_name, version, ok))

        if not rows:
            lines.append("(no optional dependencies declared)")
            return "\n".join(lines)

        headers = ("group", "package", "module", "version", "ok")
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(cell))

        total_width = sum(col_widths) + 2 * (len(headers) - 1) + 4
        sep = "\u2500" * total_width

        lines.append(sep)
        header_line = "  ".join(h.ljust(w) for h, w in zip(headers, col_widths, strict=True))
        lines.append(header_line)
        for row in rows:
            lines.append("  ".join(cell.ljust(w) for cell, w in zip(row, col_widths, strict=True)))
        lines.append(sep)

        available = sum(1 for r in rows if r[4] == "\u2713")
        lines.append(f"available: {available}/{len(rows)}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        available = sum(1 for e in self._data.values() if e.get("available"))
        total = len(self._data)
        return f"Pantry({available}/{total} available)"
