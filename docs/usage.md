# Usage Guide

This page covers all the access patterns Pantry provides.

Pantry has **two distinct purposes**:

1. **External dependencies** — probe optional packages from `pyproject.toml`
   (`has`, `get`, `pantry["pillow"]`, `report`, decorator)
2. **Own modules — lazy import** — defer imports of your own project modules
   to break circular dependencies (`lazy_import`, `pantry["myapp.models.User"]`)

These two systems are separate. `has()`, `get()`, and `report()` only know
about external dependencies. Lazy imports are accessed exclusively via
`pantry["dotted.path"]`.

---

## Part 1: External Dependencies

### Importing Modules

Pantry gives you two ways to import optional modules: **strict** and **safe**.

### Strict Import — `pantry[pkg]`

Use subscript syntax when the dependency is required for the current code path.
Raises `RuntimeError` with a clear install instruction if the package is missing.

```python
import pantry

PIL = pantry["pillow"]
img = PIL.Image.open("photo.jpg")
```

If `pillow` is not installed:

```text
RuntimeError: Package 'pillow' is not available. Install with: pip install pillow
```

This is the recommended pattern when you **know** the package must be present
for the function to work.

### Safe Import — `pantry.get(pkg)`

Use `get()` when you want to handle the missing-package case yourself.

```python
import pantry

np = pantry.get("numpy")
if np is not None:
    arr = np.array([1, 2, 3])
else:
    # fallback implementation without numpy
    arr = [1, 2, 3]
```

You can provide a default value:

```python
# Returns None if missing (default)
np = pantry.get("numpy")

# Returns a custom default if missing
redis = pantry.get("redis", None)
sentinel = object()
mod = pantry.get("exotic-pkg", sentinel)
```

### Comparison

| Pattern | Missing package | Use when |
| ------- | --------------- | -------- |
| `pantry["pkg"]` | `RuntimeError` with install instructions | Feature requires the package |
| `pantry.get("pkg")` | Returns `None` | You have a fallback |
| `pantry.get("pkg", default)` | Returns *default* | You need a specific sentinel |

---

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
    # both are installed — safe to use
    np = pantry["numpy"]
    pd = pantry["pandas"]
```

### Groups

Check whether at least one package in a dependency group is available:

```python
if pantry.has_group("imaging"):
    # at least one of pillow, wand, etc. is installed
    ...
```

Groups correspond to the keys in `[project.optional-dependencies]`:

```toml
[project.optional-dependencies]
imaging = ["pillow>=10.0", "wand"]    # pantry.has_group("imaging")
data = ["numpy>=1.24", "pandas>=2.0"] # pantry.has_group("data")
```

`has_group()` uses **any** semantics (at least one), while `has()` uses
**all** semantics (every listed package must be present).

---

## Decorator

Guard functions so they fail at call-time — not import-time — with a clear message:

```python
import pantry

@pantry("numpy", "pandas")
def analyze(data):
    np = pantry["numpy"]
    pd = pantry["pandas"]
    df = pd.DataFrame(data)
    return np.mean(df.values)
```

If called when `pandas` is missing:

```text
RuntimeError: analyze requires: pandas. Install with: pip install pandas
```

### Why at call-time?

The module can be imported without error even if some optional dependencies
are missing. The error only fires when the guarded function is actually called.
This is important for libraries where different users may have different
optional packages installed.

### Metadata preservation

The decorator uses `functools.wraps`, so `__name__`, `__doc__`, `__module__`,
and `__qualname__` are preserved:

```python
@pantry("numpy")
def my_function():
    """My docstring."""
    ...

assert my_function.__name__ == "my_function"
assert my_function.__doc__ == "My docstring."
```

---

## Reporting

### Full Report

Get a formatted table of all probed packages:

```python
print(pantry.report())
```

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

### Quick Summary

The `repr` gives a one-line overview:

```python
>>> import pantry
>>> pantry
Pantry(3/4 available)
```

---

## Testing with simulate_missing

When testing your code, you need to verify behavior both when optional
dependencies are present and when they are missing. `simulate_missing`
provides a clean way to do this:

```python
import pantry

def test_fallback_without_numpy():
    with pantry.simulate_missing("numpy"):
        assert pantry.has("numpy") is False
        assert pantry.get("numpy") is None
        # your fallback code runs here

    # outside the context manager, numpy is available again
    assert pantry.has("numpy") is True
```

### Multiple packages

```python
with pantry.simulate_missing("numpy", "pandas"):
    assert pantry.has("numpy") is False
    assert pantry.has("pandas") is False
```

### With decorators

```python
@pantry("numpy")
def compute():
    ...

def test_decorator_fails_when_missing():
    with pantry.simulate_missing("numpy"):
        with pytest.raises(RuntimeError, match="requires: numpy"):
            compute()
```

### Exception safety

The original state is always restored, even if an exception is raised
inside the context manager.

---

## Module Name Resolution

Pantry automatically resolves pip package names to their importable module names.
You always refer to packages by their **pip name** — the mapping happens transparently.

Common examples:

| pip name | import name | How resolved |
| -------- | ----------- | ------------ |
| `pillow` | `PIL` | `top_level.txt` |
| `scikit-learn` | `sklearn` | `top_level.txt` |
| `python-dateutil` | `dateutil` | `top_level.txt` |
| `my-package` | `my_package` | hyphen → underscore fallback |

### Resolution Order

1. **`top_level.txt`** from distribution metadata (most reliable)
2. **Top-level `__init__.py`** in the distribution's installed files
3. **Top-level `.py` files** (non-private) in the distribution's installed files
4. **Fallback**: replace hyphens with underscores

This covers the vast majority of packages on PyPI without any manual configuration.

---

## Part 2: Lazy Import — Breaking Circular Dependencies

This is a separate feature for your **own project modules**, not for external
dependencies. It defers the actual import until first access, breaking
circular import chains.

### The Problem

```python
# module_a.py
from myapp.module_b import Helper   # <-- module_b tries to import module_a → cycle!

class Service:
    def run(self):
        return Helper()
```

### The Solution

```python
# module_a.py
import pantry

pantry.lazy_import("myapp.module_b.Helper")

class Service:
    def run(self):
        Helper = pantry["myapp.module_b.Helper"]  # import happens here
        return Helper()
```

At the top level, `lazy_import` just registers the name — no import occurs.
When `pantry["myapp.module_b.Helper"]` is called later (inside a method),
both modules are fully loaded and there is no cycle.

### Dotted Paths

`lazy_import` resolves dotted paths intelligently:

| Path | Resolves to |
| ---- | ----------- |
| `"json"` | The `json` module |
| `"PIL.Image"` | The `Image` submodule of PIL |
| `"collections.OrderedDict"` | The `OrderedDict` class |
| `"myapp.models.User"` | The `User` class in `myapp.models` |

Resolution strategy:

1. Try `importlib.import_module(path)` — works for modules and submodules
2. If that fails, import the parent and use `getattr` for the last component — works for classes, functions, constants

### Multiple Registrations

```python
pantry.lazy_import(
    "myapp.models.User",
    "myapp.db.Session",
    "myapp.utils.format_date",
)
```

### Caching

The result is cached on first access. Subsequent `pantry["path"]` calls
return the same object without re-importing.

### Separation from External Dependencies

Lazy imports and external dependency probes are **completely separate**:

| Operation | External deps | Lazy imports |
| --------- | ------------- | ------------ |
| `pantry.has("x")` | Checks pyproject.toml | Ignores lazy |
| `pantry.get("x")` | Returns module or None | Ignores lazy |
| `pantry["x"]` | Checks probe data | **Also** checks lazy (priority) |
| `pantry.report()` | Shows all probed packages | Ignores lazy |
| `@pantry("x")` | Guards with probe data | Ignores lazy |

`pantry["key"]` is the **only** accessor that works for both systems.
Lazy imports take priority if the same key exists in both.

### Relationship to PEP 690

This feature is a lightweight bridge toward [PEP 690](https://peps.python.org/pep-0690/)
(Lazy Imports), which will make all imports lazy at the interpreter level.
Until PEP 690 is widely available, `pantry.lazy_import()` provides the key
benefit — breaking circular imports — with minimal ceremony.

When PEP 690 arrives, migration is straightforward: remove the `lazy_import()`
calls and replace `pantry["path"]` with standard imports.

---

## Next Steps

- {doc}`api` — full API reference with signatures and types
- {doc}`architecture` — how Pantry works internally
