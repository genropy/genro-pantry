# Pantry

[![GitHub](https://img.shields.io/badge/GitHub-genro--pantry-blue?logo=github)](https://github.com/genropy/genro-pantry)
[![PyPI](https://img.shields.io/pypi/v/mypantry)](https://pypi.org/project/mypantry/)
[![Python](https://img.shields.io/pypi/pyversions/mypantry)](https://pypi.org/project/mypantry/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](https://github.com/genropy/genro-pantry/blob/main/LICENSE)

**Runtime capability registry for optional Python dependencies.**

Pantry discovers optional dependency groups declared in `pyproject.toml`,
probes which packages are actually installed, and exposes a clean API
to check availability, import modules safely, and guard functions via decorators.

## Why Pantry?

When your library supports optional features powered by third-party packages,
you need a clean way to:

- Check what's installed at runtime
- Import optional modules safely
- Fail with clear error messages when a feature is used but its dependency is missing
- Show users which optional packages are available

Pantry handles all of this with zero configuration — just declare your
optional dependencies in `pyproject.toml` as you normally would.

## At a Glance

```python
import pantry

# Direct import — raises RuntimeError if missing
PIL = pantry["pillow"]

# Safe import — returns None if missing
np = pantry.get("numpy")

# Check before use
if pantry.has("redis"):
    redis = pantry["redis"]

# Guard a function
@pantry("numpy", "pandas")
def analyze(data):
    ...

# See what's available
print(pantry.report())
```

```{toctree}
:maxdepth: 2
:caption: Guide
:hidden:

getting-started
usage
```

```{toctree}
:maxdepth: 2
:caption: Reference
:hidden:

api
architecture
```

```{toctree}
:maxdepth: 1
:caption: Project
:hidden:

changelog
```
