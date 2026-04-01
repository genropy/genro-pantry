# Design Philosophy

## Pure Syntactic Sugar

mypantry does not do anything you can't do with the standard library.
It is syntactic sugar over `importlib.metadata` and `importlib.import_module`.

What it saves you: scattered try/except blocks, boolean flags, inconsistent
error messages, manual module name resolution.

## Extreme Lightness

~300 lines of Python in one file. Zero external dependencies.

| File | Lines | Purpose |
| ---- | ----: | ------- |
| `__init__.py` | 25 | Module-as-instance bootstrap |
| `_registry.py` | 303 | The entire public API |
| **Total** | **328** | |

Every line earns its place.

## Zero Configuration

No config files. No pyproject.toml scanning. No setup calls. No plugin
registration. `import pantry` and go.

This was a deliberate architectural change in v0.5.0. Earlier versions
depended on `pyproject.toml`, which broke when the package was installed
(Docker, pip install). Now Pantry uses `importlib.metadata` directly —
it works in any context where Python runs.

## Zero Magic

- No monkey-patching of `sys.meta_path` or import hooks
- No background threads or async operations
- No lazy loading of external deps — `has()` is a metadata check, `get()`/`[]` do a real import
- The one "magic" thing: `sys.modules[__name__] = instance` (well-known Python idiom)

## Clear Error Messages

```text
RuntimeError: Package 'pillow' is not available. Install with: pip install pillow
```

```text
RuntimeError: analyze requires: pandas. Install with: pip install pandas
```

No stack traces to decode. The error tells you what is missing and how to fix it.

## Two Distinct Purposes

1. **External dependencies** — check and import any installed package
2. **Own modules (lazy import)** — break circular imports by deferring resolution

These share the `pantry["key"]` accessor but are otherwise independent.
`has()`, `get()`, `report()` only operate on external dependencies.

## Bridge, Not Framework

The lazy import feature is a bridge toward PEP 690. When PEP 690 is available:

```python
# Before
pantry.lazy_import("myapp.models.User")
User = pantry["myapp.models.User"]

# After (PEP 690)
from myapp.models import User
```

mypantry does not try to be a complete lazy import framework.
