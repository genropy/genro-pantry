# Pantry

[![PyPI version](https://img.shields.io/pypi/v/mypantry?cacheSeconds=300)](https://pypi.org/project/mypantry/)
[![Tests](https://github.com/genropy/genro-pantry/actions/workflows/tests.yml/badge.svg)](https://github.com/genropy/genro-pantry/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/genropy/genro-pantry/branch/main/graph/badge.svg)](https://codecov.io/gh/genropy/genro-pantry)
[![Documentation](https://readthedocs.org/projects/mypantry/badge/?version=latest)](https://mypantry.readthedocs.io/en/latest/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Pantry** is a runtime capability registry for optional Python dependencies. It discovers dependency groups from your `pyproject.toml`, probes which packages are actually installed, and gives you a clean API to check availability, import modules safely, and guard functions with decorators.

## Why Pantry?

When your library supports optional features powered by third-party packages, you need to:

| Problem | Without Pantry | With Pantry |
| ------- | -------------- | ----------- |
| Check if a package is installed | `try: import pkg` scattered everywhere | `pantry.has("pkg")` |
| Import with fallback | Repeated try/except blocks | `pantry.get("pkg")` |
| Fail with clear message | Custom error handling per feature | `pantry["pkg"]` raises with install instructions |
| Guard a function | Manual checks at every entry point | `@pantry("pkg1", "pkg2")` |
| Show what's available | Roll your own reporting | `pantry.report()` |

**Zero configuration** — just declare optional dependencies in `pyproject.toml` as you normally would.

## Installation

```bash
pip install mypantry
```

Only runtime dependency: `packaging` (454 KB, zero transitive deps, already present in most Python environments).

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
group     package  module  version  ok
imaging   pillow   PIL     10.4.0   ✓
imaging   wand     wand    -        ✗
data      numpy    numpy   1.26.4   ✓
data      pandas   pandas  2.1.4    ✓
──────────────────────────────────────────────────────
available: 3/4
```

## How It Works

Pantry reads your standard `pyproject.toml` optional dependencies:

```toml
[project.optional-dependencies]
imaging = ["pillow>=10.0", "wand"]
data = ["numpy>=1.24", "pandas>=2.0"]
cache = ["redis>=5.0"]
```

When you `import pantry`, the module:

1. Walks up from cwd to find `pyproject.toml`
2. Reads `[project.optional-dependencies]`
3. Probes each package (installed? importable? version?)
4. Replaces itself with a `Pantry` instance — so you use it directly

Smart module name resolution handles the pip-name-to-import-name mapping automatically (`pillow` → `PIL`, `scikit-learn` → `sklearn`, etc.).

## Explicit Construction

When you need to target a specific `pyproject.toml`:

```python
from pantry import Pantry

p = Pantry.from_pyproject("path/to/pyproject.toml")
p = Pantry.discover(start="/my/project")
```

## API Summary

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

## Key Features

1. **Zero config** — reads standard `pyproject.toml`, no extra files or setup
2. **Module-as-instance** — `import pantry` gives you a ready-to-use object
3. **Smart resolution** — pip names mapped to import names automatically
4. **Multiple access patterns** — strict (`[]`), safe (`.get()`), check (`.has()`)
5. **Decorator guards** — fail at call-time with clear install instructions
6. **Group awareness** — check entire dependency groups at once
7. **Availability report** — formatted table for diagnostics
8. **Fully typed** — PEP 561 `py.typed` marker included

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
│   ├── __init__.py       # Module-as-instance bootstrap
│   ├── _discovery.py     # pyproject.toml discovery and parsing
│   ├── _probe.py         # Package probing and module name resolution
│   ├── _registry.py      # Pantry class (query, decorator, report)
│   └── py.typed          # PEP 561 marker
├── tests/
├── docs/
├── pyproject.toml
└── LICENSE
```

## Project Status

- **Status**: Alpha
- **Python**: 3.11, 3.12, 3.13
- **License**: Apache 2.0

## Contributing

Contributions are welcome. Please open an issue first to discuss what you'd like to change.

## License

Copyright 2025 Softwell S.r.l. — Licensed under the [Apache License 2.0](LICENSE).
