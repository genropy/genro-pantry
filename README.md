# Pantry

Runtime capability registry for optional Python dependencies.

Pantry discovers optional dependency groups declared in `pyproject.toml`, probes which packages are actually installed, and exposes a clean API to check availability and guard functions via decorators.

## Installation

```bash
pip install mypantry
```

## Quick start

```python
import pantry

# Subscript access — raises if missing
PIL = pantry["pillow"]
img = PIL.Image.open("photo.jpg")

# Safe access — returns None (or a default) if missing
np = pantry.get("numpy")
redis = pantry.get("redis", None)

# Check availability
if pantry.has("pillow"):
    ...

# Check multiple packages at once
if pantry.has("numpy", "pandas"):
    ...

# Guard a function via decorator
@pantry("numpy", "pandas")
def analyze(data):
    import numpy as np
    import pandas as pd
    ...

# Print a summary
print(pantry.report())
```

### Explicit construction

When you need a `Pantry` instance from a specific `pyproject.toml`:

```python
from pantry import Pantry

p = Pantry.from_pyproject("path/to/pyproject.toml")
p = Pantry.discover()  # walks upward from cwd
```

## API

### Module-level usage

`import pantry` returns a `Pantry` instance that auto-discovers your `pyproject.toml`.

### `pantry[pkg]`

Return the imported module. Raises `RuntimeError` if the package is not available.

### `pantry.get(pkg, default=None) -> module | None`

Return the imported module, or *default* if the package is not available.

### `pantry.has(*pkgs) -> bool`

True if all listed packages are installed and importable.

### `pantry.has_group(group) -> bool`

True if at least one package in the named group is available.

### `pantry(*pkgs)`

Decorator. Raises `RuntimeError` at call time if any listed package is missing.

### `pantry.report() -> str`

Formatted table of all probed packages with availability status.

### `Pantry.discover(start=None)`

Find `pyproject.toml` by walking upward from `start` (default: cwd), then probe all optional dependencies.

### `Pantry.from_pyproject(path)`

Parse a specific `pyproject.toml` and probe.

## Requirements

- Python 3.11+
- `packaging` (only runtime dependency)

## License

Apache License 2.0
