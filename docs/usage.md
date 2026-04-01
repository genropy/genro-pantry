# Usage Guide

## Checking Availability

### Single Package

```python
import pantry

if pantry.has("numpy"):
    import numpy as np
```

`has()` checks distribution metadata only — it does **not** import the module.
This is fast and safe to call at module top level.

### Multiple Packages

```python
if pantry.has("numpy", "pandas"):
    import numpy as np
    import pandas as pd
```

Returns `True` only if **all** listed packages are installed.

---

## Importing Modules

### Strict Import — `pantry[pkg]`

Raises `RuntimeError` with install instructions if the package is missing:

```python
PIL = pantry["pillow"]
```

If `pillow` is not installed:

```text
RuntimeError: Package 'pillow' is not available. Install with: pip install pillow
```

### Safe Import — `pantry.get(pkg)`

Returns `None` (or a custom default) if the package is missing:

```python
np = pantry.get("numpy")
redis = pantry.get("redis", None)
```

### Comparison

| Pattern | Missing package | Use when |
| ------- | --------------- | -------- |
| `if pantry.has("pkg"): import pkg` | Import skipped | Guard at top of file |
| `pantry["pkg"]` | `RuntimeError` | Feature requires the package |
| `pantry.get("pkg")` | Returns `None` | You have a fallback |

---

## Decorator

Guard functions so they fail at call-time with a clear message:

```python
@pantry("numpy", "pandas")
def analyze(data):
    import numpy as np
    import pandas as pd
    ...
```

Or with the recommended pattern (imports at top level):

```python
if pantry.has("numpy"):
    import numpy as np
if pantry.has("pandas"):
    import pandas as pd

@pantry("numpy", "pandas")
def analyze(data):
    df = pd.DataFrame(data)
    return np.mean(df.values)
```

The decorator preserves `__name__`, `__doc__`, and other function metadata.

---

## Version Checking

```python
ver = pantry.version("numpy")   # "1.26.4" or None
```

---

## Reporting

### Check Specific Packages

```python
print(pantry.report("numpy", "pandas", "pillow", "redis"))
```

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

### Report All Queried Packages

```python
# After using has(), get(), or []
print(pantry.report())
```

Shows all packages you have queried during the session.

---

## Module Name Resolution

Pantry automatically resolves pip package names to their importable module names.

| pip name | import name | How resolved |
| -------- | ----------- | ------------ |
| `pillow` | `PIL` | `top_level.txt` |
| `scikit-learn` | `sklearn` | `top_level.txt` |
| `python-dateutil` | `dateutil` | `top_level.txt` |
| `my-package` | `my_package` | hyphen → underscore fallback |

---

## Lazy Import — Breaking Circular Dependencies

A separate feature for **your own project modules**. Does **not** make
external dependencies lazy.

### The Problem

```python
# myapp/module_a.py
from myapp.module_b import Helper   # module_b imports module_a -> circular!
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

Lazy imports are accessed via `pantry["dotted.path"]` only. `has()`, `get()`,
and `report()` do not interact with them.

Bridge toward [PEP 690](https://peps.python.org/pep-0690/).

---

## Testing with simulate_missing

```python
def test_fallback():
    with pantry.simulate_missing("numpy"):
        assert pantry.has("numpy") is False
        assert pantry.get("numpy") is None
    assert pantry.has("numpy") is True
```

Works with decorators too:

```python
@pantry("numpy")
def compute():
    ...

def test_missing():
    with pantry.simulate_missing("numpy"):
        with pytest.raises(RuntimeError):
            compute()
```

Exception-safe — original state is always restored.

---

## Next Steps

- {doc}`api` — full API reference
- {doc}`architecture` — how it works internally
