# API Reference

## Module-Level Instance

```python
import pantry
```

Importing `pantry` returns a `Pantry` instance that has auto-discovered
your `pyproject.toml`. All methods below are available directly on this object.

---

## `pantry[pkg]`

```python
PIL = pantry["pillow"]
```

Return the imported module for *pkg*.
Raises `RuntimeError` if the package is not installed or not importable.

**Parameters:**
: `pkg` (str) — pip package name

**Returns:**
: `types.ModuleType`

**Raises:**
: `RuntimeError` — if the package is not available

---

## `pantry.get(pkg, default=None)`

```python
np = pantry.get("numpy")
redis = pantry.get("redis", "fallback")
```

Return the imported module for *pkg*, or *default* if the package is not available.

**Parameters:**
: `pkg` (str) — pip package name
: `default` (object, optional) — value to return when unavailable. Defaults to `None`.

**Returns:**
: `types.ModuleType | None` — the module, or *default*

---

## `pantry.has(*pkgs)`

```python
pantry.has("pillow")             # single
pantry.has("numpy", "pandas")    # multiple — all must be available
```

Return `True` if all listed packages are installed and importable.

**Parameters:**
: `*pkgs` (str) — one or more pip package names

**Returns:**
: `bool`

---

## `pantry.has_group(group)`

```python
pantry.has_group("imaging")
```

Return `True` if at least one package in the named dependency group is available.

Groups correspond to the keys in `[project.optional-dependencies]`.

**Parameters:**
: `group` (str) — group name from pyproject.toml

**Returns:**
: `bool`

---

## `pantry(*pkgs)` — Decorator

```python
@pantry("pillow", "numpy")
def process(path):
    ...
```

Decorator that guards a function behind one or more packages.
At call-time, raises `RuntimeError` if any of the listed packages are missing.

The error message includes the missing package names and a `pip install` command.

**Parameters:**
: `*pkgs` (str) — one or more pip package names

**Returns:**
: decorated function (metadata preserved via `functools.wraps`)

---

## `pantry.report()`

```python
print(pantry.report())
```

Return a formatted summary table of all probed packages with columns:
group, package, module, version, ok.

**Returns:**
: `str`

---

## `Pantry` Class

For explicit construction when you need control over discovery.

### `Pantry.discover(start=None)`

```python
from pantry import Pantry
p = Pantry.discover()
p = Pantry.discover(start="/my/project")
```

Find `pyproject.toml` by walking upward from *start* (default: cwd),
then probe all optional dependencies.

**Parameters:**
: `start` (Path | None) — directory to start searching from

**Returns:**
: `Pantry`

**Raises:**
: `FileNotFoundError` — if no `pyproject.toml` is found

### `Pantry.from_pyproject(path)`

```python
p = Pantry.from_pyproject("path/to/pyproject.toml")
```

Parse a specific `pyproject.toml` and probe every listed optional dependency.

**Parameters:**
: `path` (str | Path) — path to pyproject.toml

**Returns:**
: `Pantry`
