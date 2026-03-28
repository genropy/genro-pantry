# Design Philosophy

## Extreme Lightness

mypantry is ~400 lines of Python code. This is not a limitation — it is a design goal.

The entire implementation fits in four small files:

| File | Lines | Purpose |
| ---- | ----: | ------- |
| `__init__.py` | 33 | Module-as-instance bootstrap |
| `_discovery.py` | 34 | Find and parse `pyproject.toml` |
| `_probe.py` | 97 | Probe packages and resolve import names |
| `_registry.py` | 247 | The entire public API |
| **Total** | **411** | |

Every line earns its place. There is no framework, no plugin system, no abstract base
classes, no configuration format to learn. If you can read Python, you can understand
all of mypantry in 15 minutes.

## Zero Magic Where Possible

mypantry avoids implicit behavior:

- **No monkey-patching** — does not modify `sys.meta_path`, import hooks, or any global state
  (besides the standard `sys.modules` replacement for the module-as-instance pattern)
- **No background threads** — probing happens synchronously at import time
- **No lazy loading of external deps** — when you call `pantry["pillow"]`, the module
  is already probed and imported. The result is immediate.
- **No configuration files** — reads `pyproject.toml`, which already exists in your project

The one "magical" thing is the module-as-instance pattern (`sys.modules[__name__] = instance`).
This is a well-known Python idiom used by projects like `six`, `wrapt`, and others.

## Two Distinct Purposes

mypantry serves two separate needs through one unified `pantry["key"]` accessor:

### 1. External Dependencies (pyproject.toml)

For third-party packages listed in `[project.optional-dependencies]`:

```python
import pantry

PIL = pantry["pillow"]        # probed at import time
pantry.has("numpy")           # check availability
pantry.report()               # see everything
```

Accessed via: `[]`, `.get()`, `.has()`, `.has_group()`, `.report()`, decorator

### 2. Own Modules (lazy import)

For your own project modules, to break circular imports:

```python
import pantry

pantry.lazy_import("myapp.models.User")
User = pantry["myapp.models.User"]   # imported on first access
```

Accessed via: `.lazy_import()` to register, `[]` to resolve

These two systems are **completely independent**. `has()`, `get()`, `report()`,
and the decorator only operate on external dependencies. Lazy imports are a
separate registry with separate semantics.

## Clear Error Messages

When something goes wrong, the user should know exactly what to do:

```text
RuntimeError: Package 'pillow' is not available. Install with: pip install pillow
```

```text
RuntimeError: analyze requires: pandas, numpy. Install with: pip install pandas numpy
```

```text
RuntimeError: Lazy import failed: 'myapp.models' has no attribute 'Userr'
```

No stack traces to decode, no cryptic messages. The error tells you what is missing
and how to fix it.

## Bridge, Not Framework

The lazy import feature is explicitly a bridge toward
[PEP 690](https://peps.python.org/pep-0690/) (Lazy Imports). When PEP 690
becomes widely available, migration is mechanical:

```python
# Before (with mypantry)
pantry.lazy_import("myapp.models.User")
User = pantry["myapp.models.User"]

# After (with PEP 690 / native lazy imports)
from myapp.models import User
```

mypantry does not try to be a complete lazy import framework. It solves the
specific, practical problem of circular imports with minimal ceremony.
