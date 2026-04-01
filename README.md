# mypantry

[![PyPI version](https://img.shields.io/pypi/v/mypantry)](https://pypi.org/project/mypantry/)
[![Tests](https://github.com/genropy/genro-pantry/actions/workflows/tests.yml/badge.svg)](https://github.com/genropy/genro-pantry/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/genropy/genro-pantry/branch/main/graph/badge.svg)](https://codecov.io/gh/genropy/genro-pantry)
[![Documentation](https://readthedocs.org/projects/mypantry/badge/?version=latest)](https://mypantry.readthedocs.io/en/latest/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**mypantry** is lightweight syntactic sugar (~300 lines, zero dependencies) for working with optional Python packages at runtime. It wraps `importlib.metadata` to check availability, import modules safely, and guard functions with decorators.

Works everywhere — development, installed packages, Docker containers. No configuration files needed.

The entire source is one file: [`_registry.py`](src/pantry/_registry.py). Read it in 10 minutes.

## Why mypantry?

| Without mypantry | With mypantry |
| ---------------- | ------------- |
| `try: import pkg` + flag + if/raise | `pantry.has("pkg")` |
| Repeated try/except blocks | `pantry.get("pkg")` |
| Custom error handling per feature | `pantry["pkg"]` raises with install instructions |
| Manual checks at every entry point | `@pantry("pkg1", "pkg2")` |
| Move imports inside functions for circular deps | `pantry.lazy_import("my.module.Class")` |

## Use Cases

- **Libraries with optional features** — data science, ML, web frameworks with pluggable backends
- **Industrial/enterprise applications** — different sites have different hardware (printers, PLC, barcode readers, scales) each with its own optional driver package
- **Projects with circular imports** — interconnected modules that need deferred resolution
- **Any codebase** where optional dependencies vary by deployment environment

## Installation

```bash
pip install mypantry
```

**Zero dependencies.** Only Python standard library (`importlib.metadata`).

## Recommended Pattern

```python
import pantry

# Guard imports at the top of the file
if pantry.has("numpy"):
    import numpy as np

if pantry.has("pillow"):
    from PIL import Image

# Guard functions with the decorator
@pantry("numpy", "pillow")
def process(path):
    img = Image.open(path)
    return np.array(img)
```

This pattern gives you:
- **pipreqs** sees the real imports and detects dependencies correctly
- **IDE autocompletion** works because the imports are standard Python
- **pantry** provides clean error messages if a dependency is missing

## Quick Start

```python
import pantry

# Check if a package is installed (metadata only, no import)
pantry.has("numpy")                    # True/False
pantry.has("numpy", "pandas")          # True only if ALL installed

# Import a module — raises RuntimeError with install instructions if missing
PIL = pantry["pillow"]

# Import safely — returns None (or a default) if missing
np = pantry.get("numpy")
redis = pantry.get("redis", None)

# Get version
pantry.version("numpy")                # "1.26.4" or None

# Guard a function
@pantry("numpy", "pandas")
def analyze(data):
    ...

# See what you've checked
print(pantry.report())
# Or check specific packages
print(pantry.report("numpy", "pandas", "pillow", "redis"))
```

Output of `report()`:

```text
pantry report
──────────────────────────────────────────────
package  module  version  ok
numpy    numpy   1.26.4   ✓
pandas   pandas  2.1.4    ✓
pillow   PIL     10.4.0   ✓
redis    redis   -        ✗
──────────────────────────────────────────────
available: 3/4
```

## Configuration-Driven Imports

When the package name comes from configuration, pantry loads it dynamically:

```python
# The driver name comes from site/customer config
driver_name = config.get("printer_driver")   # "zebra-driver"
driver = pantry[driver_name]                  # import or RuntimeError
```

One line — no if/else, no try/except. If the driver is missing, the error
says exactly what to install.

## How It Works

`import pantry` creates a `Pantry` instance that probes packages **on demand** using `importlib.metadata`. No configuration files, no startup scanning.

- `has()` — checks distribution metadata only (fast, no import)
- `get()` / `[]` — imports the module lazily on first access, then caches it
- Smart module name resolution: `pillow` → `PIL`, `scikit-learn` → `sklearn`, etc.

Works in any context: development, installed packages, Docker, notebooks, REPLs.

## Lazy Import — Breaking Circular Dependencies

A separate feature for **your own project modules**: deferred imports that break circular dependency chains.

```python
# myapp/module_a.py
import pantry

pantry.lazy_import("myapp.module_b.Helper")

class Service:
    def run(self):
        Helper = pantry["myapp.module_b.Helper"]  # import happens here
        return Helper()
```

This does **not** make external dependencies lazy. It is specifically for breaking circular imports between your own modules. Bridge toward [PEP 690](https://peps.python.org/pep-0690/).

> Lazy imports are separate from external dependencies. `has()`, `get()`, `report()` do not interact with them.

## Testing with simulate_missing

```python
def test_fallback():
    with pantry.simulate_missing("numpy"):
        assert pantry.has("numpy") is False
    assert pantry.has("numpy") is True
```

## API Summary

### External Dependencies

| Syntax | Description |
| ------ | ----------- |
| `pantry.has("pkg")` | `True` if installed (metadata check, no import) |
| `pantry.has("p1", "p2")` | `True` if **all** are installed |
| `pantry["pkg"]` | Import module; raise `RuntimeError` if missing |
| `pantry.get("pkg")` | Import module; return `None` if missing |
| `pantry.get("pkg", default)` | Import module; return *default* if missing |
| `pantry.version("pkg")` | Installed version string, or `None` |
| `@pantry("p1", "p2")` | Decorator; `RuntimeError` at call-time if missing |
| `pantry.report(...)` | Formatted availability table |

### Lazy Import (own modules)

| Syntax | Description |
| ------ | ----------- |
| `pantry.lazy_import("a.b.C")` | Register for deferred import |
| `pantry["a.b.C"]` | Resolve on first access (cached) |

### Testing

| Syntax | Description |
| ------ | ----------- |
| `with pantry.simulate_missing("pkg")` | Temporarily hide packages |

## Key Features

1. **Zero dependencies** — pure Python standard library
2. **~300 lines** — one file, fully readable
3. **No configuration** — no pyproject.toml scanning, works everywhere
4. **On-demand probing** — `import pantry` is instant, no startup cost
5. **Smart resolution** — pip names mapped to import names automatically
6. **Multiple access patterns** — strict (`[]`), safe (`.get()`), check (`.has()`)
7. **Decorator guards** — fail at call-time with clear install instructions
8. **Lazy import** — break circular dependencies in your own modules
9. **simulate_missing** — context manager for testing fallback behavior
10. **Fully typed** — PEP 561 `py.typed` marker included

## Documentation

Full documentation: [mypantry.readthedocs.io](https://mypantry.readthedocs.io)

## Testing

```bash
pip install mypantry[dev]
pytest
```

## Repository Structure

```text
genro-pantry/
├── src/pantry/
│   ├── __init__.py       # Module-as-instance bootstrap (25 lines)
│   ├── _registry.py      # The entire API (303 lines)
│   └── py.typed          # PEP 561 marker
├── tests/                # 432 lines, 57 tests, 87% coverage
├── docs/
├── pyproject.toml
└── LICENSE
```

## Project Status

- **Status**: Beta
- **Python**: 3.11, 3.12, 3.13
- **License**: MIT

## Contributing

Contributions and feedback welcome. Please open an issue first.

## License

Copyright (c) 2025 Softwell S.r.l. — [MIT License](LICENSE).
