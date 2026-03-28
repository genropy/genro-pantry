# mypantry

[![PyPI version](https://img.shields.io/pypi/v/mypantry?cacheSeconds=300)](https://pypi.org/project/mypantry/)
[![Tests](https://github.com/genropy/genro-pantry/actions/workflows/tests.yml/badge.svg)](https://github.com/genropy/genro-pantry/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/genropy/genro-pantry/branch/main/graph/badge.svg)](https://codecov.io/gh/genropy/genro-pantry)
[![Documentation](https://readthedocs.org/projects/mypantry/badge/?version=latest)](https://mypantry.readthedocs.io/en/latest/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**mypantry** is a lightweight (~400 lines of code) runtime capability registry for optional Python dependencies. It discovers dependency groups from your `pyproject.toml`, probes which packages are actually installed, and gives you a clean API to check availability, import modules safely, and guard functions with decorators.

The entire source code is intentionally small and readable. You are encouraged to read it: [`_registry.py`](src/pantry/_registry.py) + [`_probe.py`](src/pantry/_probe.py) are all you need to understand how it works.

## Why mypantry?

When your library supports optional features powered by third-party packages, you need to:

| Problem | Without mypantry | With mypantry |
| ------- | ---------------- | ------------- |
| Check if a package is installed | `try: import pkg` scattered everywhere | `pantry.has("pkg")` |
| Import with fallback | Repeated try/except blocks | `pantry.get("pkg")` |
| Fail with clear message | Custom error handling per feature | `pantry["pkg"]` raises with install instructions |
| Guard a function | Manual checks at every entry point | `@pantry("pkg1", "pkg2")` |
| Show what's available | Roll your own reporting | `pantry.report()` |
| Break circular imports | Move imports inside functions | `pantry.lazy_import("my.module.Class")` |

**Zero configuration** — just declare optional dependencies in `pyproject.toml` as you normally would.

## Installation

```bash
pip install mypantry
```

Only runtime dependency: [`packaging`](https://pypi.org/project/packaging/) (454 KB, zero transitive deps, already present in most Python environments).

## Setup

Declare optional dependencies in your `pyproject.toml`:

```toml
[project]
name = "my-awesome-lib"

[project.optional-dependencies]
data = ["pandas>=2.0", "numpy>=1.24"]
imaging = ["pillow>=10.0", "wand"]
ml = ["torch", "scikit-learn"]
cache = ["redis>=5.0"]
```

That's it. No configuration files, no plugin registration, no setup code.

## Quick Start

```python
import pantry

# Strict import — raises RuntimeError with install instructions if missing
PIL = pantry["pillow"]
img = PIL.Image.open("photo.jpg")

# Safe import — returns None (or a custom default) if missing
np = pantry.get("numpy")
redis = pantry.get("redis", None)

# Check availability (single or multiple)
if pantry.has("pillow"):
    ...
if pantry.has("numpy", "pandas"):  # all must be available
    ...

# Guard a function — fails at call-time, not import-time
@pantry("numpy", "pandas")
def analyze(data):
    import numpy as np
    import pandas as pd
    ...

# See what's available
print(pantry.report())
```

Output of `report()`:

```text
pantry report
──────────────────────────────────────────────────────
group     package       module   version  ok
data      pandas        pandas   2.1.4    ✓
data      numpy         numpy    1.26.4   ✓
imaging   pillow        PIL      10.4.0   ✓
imaging   wand          wand     -        ✗
ml        torch         torch    -        ✗
ml        scikit-learn  sklearn  -        ✗
cache     redis         redis    -        ✗
──────────────────────────────────────────────────────
available: 3/7
```

## How It Works

When you `import pantry`, the module:

1. Walks up from cwd to find `pyproject.toml`
2. Reads `[project.optional-dependencies]`
3. Probes each package (installed? importable? version?)
4. Replaces itself with a `Pantry` instance — so you use it directly

Smart module name resolution handles the pip-name-to-import-name mapping automatically (`pillow` -> `PIL`, `scikit-learn` -> `sklearn`, `python-dateutil` -> `dateutil`, etc.).

## Explicit Construction

When you need to target a specific `pyproject.toml`:

```python
from pantry import Pantry

p = Pantry.from_pyproject("path/to/pyproject.toml")
p = Pantry.discover(start="/my/project")
```

## Lazy Import — Breaking Circular Dependencies

Pantry has a second, independent feature for **your own project modules**: deferred
imports that break circular dependency chains.

This feature does **not** make external dependencies (numpy, torch, etc.) lazy.
It is specifically designed to break circular imports between your own modules.

### The Problem

```python
# myapp/module_a.py
from myapp.module_b import Helper   # module_b imports module_a -> circular!

class Service:
    def run(self):
        return Helper()
```

```python
# myapp/module_b.py
from myapp.module_a import Service   # module_a imports module_b -> circular!

class Helper:
    def check(self):
        return Service()
```

### The Solution

```python
# myapp/module_a.py
import pantry

pantry.lazy_import("myapp.module_b.Helper")

class Service:
    def run(self):
        Helper = pantry["myapp.module_b.Helper"]  # import happens here
        return Helper()
```

`lazy_import` just registers the name — no import occurs. The actual import
happens on first `pantry["..."]` access, when all modules are fully loaded.
Results are cached after first resolution.

This is a bridge toward [PEP 690](https://peps.python.org/pep-0690/) (Lazy Imports).
When PEP 690 becomes available, migration is straightforward: remove `lazy_import()`
calls and replace `pantry["path"]` with standard imports.

> **Note:** Lazy imports are completely separate from external dependencies.
> `has()`, `get()`, `report()`, and the decorator only know about pyproject.toml packages.

## When to Use mypantry

**Good fit:**

- Libraries with many optional features (data science, ML, web, scientific, etc.)
- Projects with interconnected modules that suffer from circular imports
- Applications that need clear "install X for feature Y" error messages
- Frameworks where different users have different optional packages installed

**Not needed:**

- Simple scripts or single-file projects
- Projects with no optional dependencies
- Projects where all dependencies are always required

## API Summary

### External Dependencies (pyproject.toml)

| Syntax | Description |
| ------ | ----------- |
| `pantry["pkg"]` | Import module; raise `RuntimeError` if missing |
| `pantry.get("pkg")` | Import module; return `None` if missing |
| `pantry.get("pkg", default)` | Import module; return *default* if missing |
| `pantry.has("pkg")` | `True` if installed and importable |
| `pantry.has("p1", "p2")` | `True` if **all** are available |
| `pantry.has_group("grp")` | `True` if **any** in group is available |
| `@pantry("p1", "p2")` | Decorator; `RuntimeError` at call-time if missing |
| `pantry.report()` | Formatted availability table |
| `Pantry.discover()` | Explicit construction from auto-discovered pyproject.toml |
| `Pantry.from_pyproject(path)` | Explicit construction from a specific file |

### Lazy Import (own modules)

| Syntax | Description |
| ------ | ----------- |
| `pantry.lazy_import("a.b.C")` | Register for deferred import |
| `pantry["a.b.C"]` | Resolve on first access (cached) |

## Key Features

1. **Lightweight** — ~400 lines of code, single dependency (`packaging`)
2. **Zero config** — reads standard `pyproject.toml`, no extra files or setup
3. **Module-as-instance** — `import pantry` gives you a ready-to-use object
4. **Smart resolution** — pip names mapped to import names automatically
5. **Multiple access patterns** — strict (`[]`), safe (`.get()`), check (`.has()`)
6. **Decorator guards** — fail at call-time with clear install instructions
7. **Group awareness** — check entire dependency groups at once
8. **Lazy import** — break circular dependencies in your own modules (PEP 690 bridge)
9. **Availability report** — formatted table for diagnostics
10. **Fully typed** — PEP 561 `py.typed` marker included

## Troubleshooting

**No `pyproject.toml` found?**
Pantry walks up from the current working directory. If no `pyproject.toml` is found
(e.g. in a REPL), an empty Pantry is created — `import pantry` never fails.
`has()` returns `False` for everything, `report()` shows "(no optional dependencies declared)".

**Non-standard import names?**
Pantry resolves pip names to import names automatically (`pillow` -> `PIL`, etc.)
using distribution metadata. This works for the vast majority of PyPI packages.
For the rare edge case, use the module's actual import name directly.

**Transitive dependencies missing?**
Pantry only probes packages explicitly listed in `[project.optional-dependencies]`.
If package A requires package B, and B is missing, Pantry reports A as unavailable
(the import fails). List the packages your code directly imports.

## Documentation

Full documentation: [mypantry.readthedocs.io](https://mypantry.readthedocs.io)

- [Getting Started](https://mypantry.readthedocs.io/en/latest/getting-started.html)
- [Usage Guide](https://mypantry.readthedocs.io/en/latest/usage.html)
- [API Reference](https://mypantry.readthedocs.io/en/latest/api.html)
- [Architecture](https://mypantry.readthedocs.io/en/latest/architecture.html)

## Testing

```bash
pip install mypantry[dev]
pytest
```

## Repository Structure

```text
genro-pantry/
├── src/pantry/
│   ├── __init__.py       # Module-as-instance bootstrap (33 lines)
│   ├── _discovery.py     # pyproject.toml discovery and parsing (34 lines)
│   ├── _probe.py         # Package probing and module name resolution (97 lines)
│   ├── _registry.py      # Pantry class — the entire API (247 lines)
│   └── py.typed          # PEP 561 marker
├── tests/                # 553 lines, 71 tests, 95% coverage
├── docs/
├── pyproject.toml
└── LICENSE
```

## Project Status

- **Status**: Beta
- **Python**: 3.11, 3.12, 3.13
- **License**: MIT

## Contributing

Contributions and feedback are welcome, especially on edge cases with lazy imports.
Please open an issue first to discuss what you'd like to change.

## License

Copyright (c) 2025 Softwell S.r.l. — [MIT License](LICENSE).
