# API Reference

## Module-Level Instance

```python
import pantry
```

Importing `pantry` returns a `Pantry` instance that has auto-discovered
your `pyproject.toml`. All methods below are available directly on this object.

---

## `pantry[key]`

```python
PIL = pantry["pillow"]                    # external dependency
User = pantry["myapp.models.User"]        # lazy-imported own module
```

Return a module or lazy-resolved object for *key*.

Checks **lazy imports first** (own modules registered via `lazy_import`),
then falls back to the **pyproject.toml probe data** (external dependencies).

**Parameters:**
: `key` (str) — pip package name or lazy-registered dotted path

**Returns:**
: `types.ModuleType` (or any object for lazy attribute access)

**Raises:**
: `RuntimeError` — if the key is not found in either system

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

## `pantry.lazy_import(*paths)` — Own Modules

```python
pantry.lazy_import("myapp.models.User")
pantry.lazy_import("myapp.db.Session", "myapp.utils.format_date")
```

Register one or more dotted paths for deferred import. No import happens
at registration time. The actual import occurs on first access via
`pantry["path"]`, and the result is cached.

**Use this for your own project modules** to break circular imports.
This is completely separate from the external dependency system (`has`, `get`, `report`).

**Parameters:**
: `*paths` (str) — one or more dotted import paths

**Returns:**
: `None`

**Resolution strategy:**

1. Try `importlib.import_module(path)` — for modules and submodules
2. If that fails, import the parent and `getattr` the last component — for classes, functions, constants

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
