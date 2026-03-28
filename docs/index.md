# mypantry

[![PyPI](https://img.shields.io/pypi/v/mypantry?cacheSeconds=300)](https://pypi.org/project/mypantry/)
[![Tests](https://github.com/genropy/genro-pantry/actions/workflows/tests.yml/badge.svg)](https://github.com/genropy/genro-pantry/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/genropy/genro-pantry/branch/main/graph/badge.svg)](https://codecov.io/gh/genropy/genro-pantry)
[![Python](https://img.shields.io/pypi/pyversions/mypantry)](https://pypi.org/project/mypantry/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A lightweight (~400 lines of code) runtime capability registry for optional Python dependencies.**

mypantry discovers optional dependency groups declared in `pyproject.toml`,
probes which packages are actually installed, and exposes a clean API
to check availability, import modules safely, and guard functions via decorators.

It also provides a lazy import mechanism to break circular dependencies
between your own project modules — a lightweight bridge toward
[PEP 690](https://peps.python.org/pep-0690/).

The source code is intentionally small and readable. You are encouraged to read it:
[`_registry.py`](https://github.com/genropy/genro-pantry/blob/main/src/pantry/_registry.py) +
[`_probe.py`](https://github.com/genropy/genro-pantry/blob/main/src/pantry/_probe.py)
are all you need to understand how it works.

---

## Why mypantry?

When your library supports optional features powered by third-party packages,
you need a clean way to:

- **Check** what's installed at runtime
- **Import** optional modules safely
- **Fail clearly** when a feature is used but its dependency is missing
- **Report** which optional packages are available
- **Break circular imports** between your own modules

mypantry handles all of this with **zero configuration** — just declare your
optional dependencies in `pyproject.toml` as you normally would.

### Without mypantry

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

### With mypantry

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

# Break circular imports in your own modules
pantry.lazy_import("myapp.module_b.Helper")
Helper = pantry["myapp.module_b.Helper"]  # import happens here

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

---

## Installation

```bash
pip install mypantry
```

Only runtime dependency: [`packaging`](https://pypi.org/project/packaging/) (454 KB, zero transitive deps, already present in most Python environments).

**Python**: 3.11, 3.12, 3.13

---

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
design-philosophy
```

### Project

```{toctree}
:maxdepth: 1

changelog
```
