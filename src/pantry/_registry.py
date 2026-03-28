# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Pantry — the capability registry."""

import functools
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

    def __init__(self, data: dict[str, dict], groups: dict[str, list[str]] | None = None):
        self._data = data
        self._groups = groups or {}

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

    def __getitem__(self, pkg: str) -> types.ModuleType:
        """Return the imported module for *pkg*; raise if unavailable.

        Usage::

            PIL = pantry["pillow"]
        """
        mod = self.get(pkg)
        if mod is None:
            raise RuntimeError(
                f"Package '{pkg}' is not available. "
                f"Install with: pip install {pkg}"
            )
        return mod

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
