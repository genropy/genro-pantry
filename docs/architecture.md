# Architecture

## Overview

Pantry is built as a small pipeline of four stages:

```mermaid
graph LR
    A[Discovery] --> B[Parsing]
    B --> C[Probing]
    C --> D[Registry]
```

**Discovery** finds `pyproject.toml` by walking upward from the current directory.
**Parsing** extracts `[project.optional-dependencies]` groups.
**Probing** checks each package: is it installed? what module name? what version?
**Registry** holds the results and exposes the query/decorator API.

## Module Structure

```
src/pantry/
├── __init__.py       # Module-as-instance bootstrap
├── _discovery.py     # find_pyproject(), parse_optional_deps()
├── _probe.py         # strip_specifier(), resolve_module_name(), probe()
├── _registry.py      # Pantry class
└── py.typed          # PEP 561 marker
```

## Module-as-Instance Pattern

The key design choice is in `__init__.py`:

```python
import sys
from ._registry import Pantry

try:
    _instance = Pantry.discover()
except FileNotFoundError:
    _instance = Pantry({}, {})

_instance.Pantry = Pantry
sys.modules[__name__] = _instance
```

After this runs, `import pantry` returns a `Pantry` instance rather than
a module object. This enables the natural syntax:

```python
import pantry
PIL = pantry["pillow"]
```

The `Pantry` class is attached as an attribute so explicit construction
is still available via `pantry.Pantry` or `from pantry import Pantry`.

## Discovery

`_discovery.py` provides two functions:

- **`find_pyproject(start)`** — walks from *start* (or cwd) upward until
  `pyproject.toml` is found. Raises `FileNotFoundError` if the root is reached.

- **`parse_optional_deps(path)`** — reads the TOML file and extracts
  `[project.optional-dependencies]` as `{group: [spec, ...]}`.

## Probing

`_probe.py` handles the mapping from pip names to Python imports:

1. **`strip_specifier(raw_spec)`** — extracts the package name from a
   PEP 508 string like `"pillow>=10.0"` → `"pillow"`.

2. **`resolve_module_name(pkg_name)`** — maps pip name to importable name.
   For example `pillow` → `PIL`, `scikit-learn` → `sklearn`.
   Uses `top_level.txt`, `dist.files`, and hyphen-to-underscore fallback.

3. **`probe(pkg_name)`** — tries to import the resolved module and returns
   a dict with `pkg_name`, `module_name`, `module`, `version`, `available`.
   Never raises.

## Registry

The `Pantry` class stores probe results and dependency groups. It exposes:

- **Query methods**: `has()`, `has_group()`, `get()`, `__getitem__`
- **Decorator**: `__call__()` for function guarding
- **Reporting**: `report()`, `__repr__()`

All query methods work with pip package names, not module names.
The module name resolution is handled transparently by the probe layer.

## Design Decisions

**No lazy probing.** All packages are probed at construction time.
This keeps the API simple and makes `report()` always complete.
The cost is negligible — probing involves metadata lookups and one `import_module` per package.

**No caching across processes.** Each `import pantry` re-probes.
This ensures the registry reflects the current environment accurately.

**Fail-safe fallback.** If no `pyproject.toml` is found, `__init__.py`
creates an empty `Pantry({}, {})` instead of raising.
This means `import pantry` never fails.

## Lazy Import Subsystem

Pantry has a second, independent subsystem for **own project modules**.
It exists to break circular imports by deferring the actual `import` until
first access.

### How It Works

```python
pantry.lazy_import("myapp.models.User")
# Registers "myapp.models.User" → _UNRESOLVED in self._lazy

User = pantry["myapp.models.User"]
# 1. Finds key in self._lazy (value is _UNRESOLVED)
# 2. Calls _resolve_lazy("myapp.models.User")
# 3. Caches the result in self._lazy
# 4. Returns it
```

Resolution uses a two-step strategy:

1. `importlib.import_module(path)` — handles submodules
2. If that fails: `importlib.import_module(parent)` + `getattr(parent, attr)` — handles classes and functions

### Separation from External Dependencies

The two systems share the `__getitem__` accessor (`pantry["key"]`) but are
otherwise completely independent:

- `self._data` — external dependencies from pyproject.toml (populated at construction)
- `self._lazy` — own modules registered via `lazy_import()` (populated on demand)

`has()`, `get()`, `report()`, and the decorator only operate on `_data`.
Lazy imports are invisible to them.

This is intentional: external dependencies are about **what's installed**,
lazy imports are about **when to import**.

### Bridge to PEP 690

This feature is a lightweight bridge toward PEP 690 (Lazy Imports).
When PEP 690 becomes available, migration is mechanical: remove `lazy_import()`
calls and replace `pantry["path"]` with standard imports.
