# mypantry

[![PyPI](https://img.shields.io/pypi/v/mypantry)](https://pypi.org/project/mypantry/)
[![Tests](https://github.com/genropy/genro-pantry/actions/workflows/tests.yml/badge.svg)](https://github.com/genropy/genro-pantry/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/genropy/genro-pantry/branch/main/graph/badge.svg)](https://codecov.io/gh/genropy/genro-pantry)
[![Python](https://img.shields.io/pypi/pyversions/mypantry)](https://pypi.org/project/mypantry/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Lightweight syntactic sugar (~300 lines, zero dependencies) for optional Python packages.**

mypantry wraps `importlib.metadata` to check package availability, import modules
safely, and guard functions with decorators. Works everywhere — development,
installed packages, Docker, notebooks, REPLs. No configuration files needed.

The entire source is one file:
[`_registry.py`](https://github.com/genropy/genro-pantry/blob/main/src/pantry/_registry.py).

---

## At a Glance

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

# Or use pantry directly
PIL = pantry["pillow"]          # raise if missing
np = pantry.get("numpy")        # None if missing
pantry.version("numpy")         # "1.26.4"
print(pantry.report("numpy", "pillow", "redis"))
```

---

## Installation

```bash
pip install mypantry
```

**Zero dependencies.** Only Python standard library.

---

## Contents

### Guide

```{toctree}
:maxdepth: 2

getting-started
usage
```

### Reference

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
