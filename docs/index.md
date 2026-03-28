# mypantry

[![PyPI](https://img.shields.io/pypi/v/mypantry?cacheSeconds=300)](https://pypi.org/project/mypantry/)
[![Tests](https://github.com/genropy/genro-pantry/actions/workflows/tests.yml/badge.svg)](https://github.com/genropy/genro-pantry/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/genropy/genro-pantry/branch/main/graph/badge.svg)](https://codecov.io/gh/genropy/genro-pantry)
[![Python](https://img.shields.io/pypi/pyversions/mypantry)](https://pypi.org/project/mypantry/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](https://github.com/genropy/genro-pantry/blob/main/LICENSE)

**Runtime capability registry for optional Python dependencies.**

Pantry discovers optional dependency groups declared in `pyproject.toml`,
probes which packages are actually installed, and exposes a clean API
to check availability, import modules safely, and guard functions via decorators.

---

## Why Pantry?

When your library supports optional features powered by third-party packages,
you need a clean way to:

- **Check** what's installed at runtime
- **Import** optional modules safely
- **Fail clearly** when a feature is used but its dependency is missing
- **Report** which optional packages are available

Pantry handles all of this with **zero configuration** — just declare your
optional dependencies in `pyproject.toml` as you normally would.

### Without Pantry

```python
# Scattered try/except blocks everywhere
try:
    import PIL
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

def resize(path):
    if not HAS_PILLOW:
        raise RuntimeError("pillow is required: pip install pillow")
    ...
```

### With Pantry

```python
import pantry

@pantry("pillow")
def resize(path):
    PIL = pantry["pillow"]
    ...
```

---

## At a Glance

```python
import pantry

# Strict import — raises RuntimeError with install instructions if missing
PIL = pantry["pillow"]

# Safe import — returns None (or a custom default) if missing
np = pantry.get("numpy")
redis = pantry.get("redis", None)

# Check availability (single or multiple)
if pantry.has("pillow"):
    ...
if pantry.has("numpy", "pandas"):  # all must be available
    ...

# Guard a function — fails at call-time with a clear message
@pantry("numpy", "pandas")
def analyze(data):
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

---

## Installation

```bash
pip install mypantry
```

Only runtime dependency: [`packaging`](https://pypi.org/project/packaging/) (454 KB, zero transitive deps, already present in most Python environments).

**Python**: 3.11, 3.12, 3.13

---

## Contents

### Guide

Step-by-step instructions to get up and running.

```{toctree}
:maxdepth: 2

getting-started
usage
```

### Reference

Detailed API documentation and design decisions.

```{toctree}
:maxdepth: 2

api
architecture
```

### Project

```{toctree}
:maxdepth: 1

changelog
```
