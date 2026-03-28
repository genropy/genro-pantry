# Usage Guide

## Importing Modules

### Strict Import — `pantry[pkg]`

Use subscript syntax when the dependency is required for the current code path.
Raises `RuntimeError` with a clear install instruction if the package is missing.

```python
import pantry

PIL = pantry["pillow"]
img = PIL.Image.open("photo.jpg")
```

If `pillow` is not installed:

```
RuntimeError: Package 'pillow' is not available. Install with: pip install pillow
```

### Safe Import — `pantry.get(pkg)`

Use `get()` when you want to handle the missing-package case yourself.

```python
import pantry

np = pantry.get("numpy")
if np is not None:
    arr = np.array([1, 2, 3])
```

You can also provide a default value:

```python
redis = pantry.get("redis", None)
```

## Checking Availability

### Single Package

```python
if pantry.has("pillow"):
    PIL = pantry["pillow"]
    # use PIL...
```

### Multiple Packages

`has()` accepts multiple arguments — returns `True` only if **all** are available:

```python
if pantry.has("numpy", "pandas"):
    # both are installed
    ...
```

### Groups

Check whether at least one package in a dependency group is available:

```python
if pantry.has_group("imaging"):
    # at least one of pillow, wand, etc. is installed
    ...
```

Groups correspond to the keys in `[project.optional-dependencies]`.

## Decorator

Guard functions so they fail at call-time with a clear message:

```python
import pantry

@pantry("numpy", "pandas")
def analyze(data):
    import numpy as np
    import pandas as pd
    df = pd.DataFrame(data)
    return np.mean(df.values)
```

If called when `pandas` is missing:

```
RuntimeError: analyze requires: pandas. Install with: pip install pandas
```

The decorator preserves `__name__`, `__doc__`, and other function metadata.

## Reporting

Get a formatted table of all probed packages:

```python
print(pantry.report())
```

```
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

The `repr` gives a quick summary:

```python
>>> import pantry
>>> pantry
Pantry(3/4 available)
```

## Module Name Resolution

Pantry automatically resolves pip package names to their importable module names.
For example, `pillow` maps to `PIL`, `scikit-learn` maps to `sklearn`.

The resolution order is:

1. `top_level.txt` from distribution metadata
2. Top-level `__init__.py` in the distribution files
3. Top-level `.py` files (non-private) in the distribution files
4. Fallback: replace hyphens with underscores (`my-package` → `my_package`)

This works transparently — you always refer to packages by their pip name.
