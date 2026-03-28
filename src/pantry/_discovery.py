# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Locate and parse pyproject.toml for optional dependency groups."""

import tomllib
from pathlib import Path


def find_pyproject(start: Path | None = None) -> Path:
    """Walk up from *start* (default: cwd) until a ``pyproject.toml`` is found.

    Raises ``FileNotFoundError`` if the filesystem root is reached without a match.
    """
    current = Path(start) if start is not None else Path.cwd()
    current = current.resolve()
    while True:
        candidate = current / "pyproject.toml"
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            raise FileNotFoundError("pyproject.toml not found in any parent directory")
        current = parent


def parse_optional_deps(path: Path) -> dict[str, list[str]]:
    """Read ``[project.optional-dependencies]`` from *path*.

    Returns ``{group: [raw_spec, ...]}`` — e.g.
    ``{"imaging": ["pillow>=9.0", "wand"], "data": ["numpy"]}``.
    Returns an empty dict when the section is absent.
    """
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
    return dict(data.get("project", {}).get("optional-dependencies", {}))
